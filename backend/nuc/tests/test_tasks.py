"""Tests for NUC Celery tasks."""
from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

from notifications.models import Notification
from nuc.tasks import check_expiring_accreditations
from nuc.tests.factories import AccreditationFactory

User = get_user_model()


@pytest.mark.django_db
class TestCheckExpiringAccreditations:
    def test_alerts_admins(self):
        """Accreditations expiring within 90 days trigger admin notifications."""
        admin = User.objects.create_user(
            username='nuc_admin',
            email='nuc_admin@test.local',
            password='TestPass12345!',
            user_type='admin',
        )
        accreditation = AccreditationFactory(
            expiry_date=date.today() + timedelta(days=30),
        )

        result = check_expiring_accreditations.apply().get()

        assert Notification.objects.filter(
            user=admin,
            title='Accreditation Expiring',
        ).exists()
        notification = Notification.objects.get(user=admin)
        assert accreditation.programme.name in notification.message
        assert '1 accreditation alerts sent' in result

    def test_no_expiring_returns_zero(self):
        """Accreditations not expiring soon produce zero alerts."""
        User.objects.create_user(
            username='nuc_admin2',
            email='nuc_admin2@test.local',
            password='TestPass12345!',
            user_type='admin',
        )
        AccreditationFactory(
            expiry_date=date.today() + timedelta(days=365),
        )

        result = check_expiring_accreditations.apply().get()
        assert result == '0 accreditation alerts sent'
