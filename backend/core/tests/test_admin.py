"""Smoke tests verifying all admin changelist pages load without errors."""
import pytest
from django.urls import reverse


def _get_registered_admin_models():
    """Discover all models registered in Django admin."""
    from django.contrib.admin.sites import site

    models = []
    for model, admin_class in site._registry.items():
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        models.append(f'{app_label}_{model_name}')
    return sorted(models)


@pytest.mark.django_db
@pytest.mark.parametrize('model_name', _get_registered_admin_models())
def test_admin_changelist_loads(admin_client, model_name):
    """Admin changelist page for every registered model returns 200."""
    url = reverse(f'admin:{model_name}_changelist')
    response = admin_client.get(url)
    assert response.status_code == 200, (
        f"Admin changelist for {model_name} returned {response.status_code}"
    )
