"""Tests for notifications service layer."""
import pytest

from notifications.exceptions import NotificationPermissionDenied
from notifications.services import (
    AnnouncementService,
    EmailService,
    NotificationService,
)
from notifications.tests.factories import (
    AnnouncementFactory,
    EmailTemplateFactory,
    NotificationFactory,
)
from accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# NotificationService
# ---------------------------------------------------------------------------

class TestNotificationService:

    def test_create_notification_persists(self):
        user = UserFactory()

        notification = NotificationService.create(
            user=user,
            level='info',
            title='Welcome',
            message='Welcome to the platform.',
            link='/dashboard',
        )

        assert notification.pk is not None
        assert notification.user == user
        assert notification.title == 'Welcome'
        assert notification.notification_type == 'info'
        assert notification.link == '/dashboard'
        assert notification.is_read is False

    def test_create_for_audience_bulk_creates(self):
        UserFactory(user_type='student')
        UserFactory(user_type='student')
        UserFactory(user_type='lecturer')
        UserFactory(user_type='admin')

        count = NotificationService.create_for_audience(
            audience=['student', 'lecturer'],
            level='warning',
            title='System Maintenance',
            message='Scheduled downtime at midnight.',
        )

        assert count == 3  # 2 students + 1 lecturer

    def test_mark_read_only_works_for_owner(self):
        owner = UserFactory()
        other = UserFactory()
        notification = NotificationFactory(user=owner)

        with pytest.raises(NotificationPermissionDenied):
            NotificationService.mark_read(notification, other)

        # Owner should succeed
        updated = NotificationService.mark_read(notification, owner)
        assert updated.is_read is True
        assert updated.read_at is not None

    def test_mark_all_read_updates_count(self):
        user = UserFactory()
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        count = NotificationService.mark_all_read(user)

        assert count == 2

    def test_unread_count_correct(self):
        user = UserFactory()
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        assert NotificationService.unread_count(user) == 2


# ---------------------------------------------------------------------------
# EmailService
# ---------------------------------------------------------------------------

class TestEmailService:

    def test_render_email_template_substitutes_context(self):
        EmailTemplateFactory(
            name='welcome_email',
            subject='Welcome $name',
            body='Dear $name, your enrollment in $topic is confirmed.',
        )

        subject, body = EmailService.render_template(
            'welcome_email',
            {'name': 'John', 'topic': 'Computer Science'},
        )

        assert subject == 'Welcome John'
        assert 'Dear John' in body
        assert 'Computer Science' in body


# ---------------------------------------------------------------------------
# AnnouncementService
# ---------------------------------------------------------------------------

class TestAnnouncementService:

    def test_announcement_for_user_filters_by_audience(self):
        admin = UserFactory(user_type='admin')
        student_user = UserFactory(user_type='student')

        # Announcement for all
        AnnouncementFactory(target_audience='all', created_by=admin)
        # Announcement for students only
        AnnouncementFactory(target_audience='students', created_by=admin)
        # Announcement for lecturers only
        AnnouncementFactory(target_audience='lecturers', created_by=admin)

        student_announcements = AnnouncementService.for_user(student_user)

        # Student should see 'all' + 'students' = 2
        assert student_announcements.count() == 2

    def test_publish_creates_published_announcement(self):
        admin = UserFactory(user_type='admin')

        announcement = AnnouncementService.publish(
            title='Holiday Notice',
            body='Campus will be closed next Monday.',
            audience='all',
            created_by=admin,
        )

        assert announcement.pk is not None
        assert announcement.is_published is True
        assert announcement.title == 'Holiday Notice'
        assert announcement.publish_date is not None
