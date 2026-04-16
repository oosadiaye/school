"""Factory Boy factories for notifications models."""
import factory
from accounts.tests.factories import UserFactory
from notifications.models import Announcement, EmailTemplate, Notification, SMSTemplate


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Notification {n}")
    message = 'This is a test notification.'
    notification_type = 'info'
    is_read = False


class EmailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    name = factory.Sequence(lambda n: f"email_template_{n}")
    subject = 'Hello $name'
    body = 'Dear $name, this is regarding $topic.'
    is_active = True


class SMSTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SMSTemplate

    name = factory.Sequence(lambda n: f"sms_template_{n}")
    message = 'Hi $name, your $topic is ready.'
    is_active = True


class AnnouncementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Announcement

    title = factory.Sequence(lambda n: f"Announcement {n}")
    message = 'This is a test announcement.'
    target_audience = 'all'
    is_published = True
    created_by = factory.SubFactory(UserFactory, user_type='admin')
