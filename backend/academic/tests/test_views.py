"""Integration tests for academic API endpoints."""
import pytest
from academic.tests.factories import AcademicSessionFactory, CourseFactory


@pytest.mark.django_db
def test_current_session_endpoint(authed_admin_client):
    AcademicSessionFactory(is_current=True)
    response = authed_admin_client.get('/api/academic/sessions/current/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_courses(authed_admin_client):
    CourseFactory()
    response = authed_admin_client.get('/api/academic/courses/')
    assert response.status_code == 200
    assert 'results' in response.data


@pytest.mark.django_db
def test_unauthenticated_cannot_create_course(api_client):
    """Write operations require auth even on IsAuthenticatedOrReadOnly views."""
    response = api_client.post('/api/academic/courses/', {})
    assert response.status_code in [401, 403]
