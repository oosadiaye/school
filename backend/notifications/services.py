"""Business logic for the notifications app."""
from __future__ import annotations

import logging
from string import Template
from typing import Sequence

from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from notifications.exceptions import NotificationPermissionDenied, TemplateNotFound
from notifications.models import Announcement, EmailTemplate, Notification, SMSTemplate

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


class NotificationService:
    """Create and manage user notifications."""

    @staticmethod
    @transaction.atomic
    def create(user, level: str, title: str, message: str, link: str | None = None) -> Notification:
        """Create a single notification for a user.

        Args:
            user: the target user.
            level: one of Notification.TYPES values (info, success, warning, error).
            title: notification title.
            message: notification body text.
            link: optional URL for the notification to link to.
        """
        return Notification.objects.create(
            user=user,
            notification_type=level,
            title=title,
            message=message,
            link=link or '',
        )

    @staticmethod
    @transaction.atomic
    def create_for_audience(
        audience: Sequence[str],
        level: str,
        title: str,
        message: str,
    ) -> int:
        """Bulk-create notifications for all users matching user_type in audience list.

        Args:
            audience: list of user_type values (e.g. ['student', 'lecturer']).
            level: notification level.
            title: notification title.
            message: notification body.

        Returns:
            Count of notifications created.
        """
        from accounts.models import User as UserModel

        users = UserModel.objects.filter(user_type__in=audience)
        notifications = [
            Notification(
                user=u,
                notification_type=level,
                title=title,
                message=message,
            )
            for u in users
        ]
        created = Notification.objects.bulk_create(notifications)
        return len(created)

    @staticmethod
    def mark_read(notification: Notification, user) -> Notification:
        """Mark a notification as read, verifying the user owns it.

        Raises NotificationPermissionDenied if user does not own the notification.
        """
        if notification.user_id != user.pk:
            raise NotificationPermissionDenied("Cannot mark another user's notification as read.")
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        notification.refresh_from_db()
        return notification

    @staticmethod
    def mark_all_read(user) -> int:
        """Mark all unread notifications for a user as read. Returns count updated."""
        return Notification.objects.filter(
            user=user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())

    @staticmethod
    def unread_count(user) -> int:
        """Return the count of unread notifications for a user."""
        return Notification.objects.filter(user=user, is_read=False).count()


class EmailService:
    """Shell email service. Phase 3 adds real sending via Celery."""

    @staticmethod
    def render_template(template_name: str, context: dict) -> tuple[str, str]:
        """Look up an EmailTemplate and substitute context variables.

        Uses Python string.Template for safe $variable substitution.

        Returns:
            Tuple of (subject, body).

        Raises:
            TemplateNotFound if no active template with the given name exists.
        """
        try:
            tpl = EmailTemplate.objects.get(name=template_name, is_active=True)
        except EmailTemplate.DoesNotExist:
            raise TemplateNotFound(f"Email template '{template_name}' not found.")

        subject = Template(tpl.subject).safe_substitute(context)
        body = Template(tpl.body).safe_substitute(context)
        return subject, body

    @staticmethod
    def queue_email(to: str, template_name: str, context: dict) -> None:
        """Queue an email for async sending via Celery.

        Renders the template synchronously, then dispatches the send
        to a background worker so the caller never blocks on SMTP I/O.
        """
        try:
            subject, body = EmailService.render_template(template_name, context)
        except TemplateNotFound:
            logger.warning("Email template '%s' not found; email to %s not queued.", template_name, to)
            return
        from notifications.tasks import send_email_task

        send_email_task.delay(to, subject, body)


class SMSService:
    """Shell SMS service. Phase 3 adds real sending."""

    @staticmethod
    def render_template(template_name: str, context: dict) -> str:
        """Look up an SMSTemplate and substitute context variables.

        Returns the rendered message body.

        Raises:
            TemplateNotFound if no active template with the given name exists.
        """
        try:
            tpl = SMSTemplate.objects.get(name=template_name, is_active=True)
        except SMSTemplate.DoesNotExist:
            raise TemplateNotFound(f"SMS template '{template_name}' not found.")

        return Template(tpl.message).safe_substitute(context)

    @staticmethod
    def queue_sms(to_phone: str, template_name: str, context: dict) -> None:
        """Queue an SMS for async sending via Celery.

        Renders the template synchronously, then dispatches the send
        to a background worker.
        """
        try:
            body = SMSService.render_template(template_name, context)
        except TemplateNotFound:
            logger.warning("SMS template '%s' not found; SMS to %s not queued.", template_name, to_phone)
            return
        from notifications.tasks import send_sms_task

        send_sms_task.delay(to_phone, body)


class AnnouncementService:
    """Create and query announcements."""

    @staticmethod
    @transaction.atomic
    def publish(
        title: str,
        body: str,
        audience: str,
        created_by,
    ) -> Announcement:
        """Publish an announcement.

        Args:
            title: announcement title.
            body: announcement body text.
            audience: one of Announcement.target_audience choices.
            created_by: the user creating the announcement.
        """
        return Announcement.objects.create(
            title=title,
            message=body,
            target_audience=audience,
            is_published=True,
            publish_date=timezone.now(),
            created_by=created_by,
        )

    @staticmethod
    def for_user(user) -> QuerySet[Announcement]:
        """Return published announcements matching the user's user_type.

        'all' audience matches every user.
        Plural forms (students->student, lecturers->lecturer, staff->staff) are
        mapped to match the user.user_type field.
        """
        audience_map = {
            'student': ['all', 'students'],
            'lecturer': ['all', 'lecturers'],
            'staff': ['all', 'staff'],
            'admin': ['all', 'staff'],
            'parent': ['all'],
        }
        matching = audience_map.get(user.user_type, ['all'])
        return Announcement.objects.filter(
            target_audience__in=matching,
            is_published=True,
        )
