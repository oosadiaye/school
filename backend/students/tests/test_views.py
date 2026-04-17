"""Integration tests for student API endpoints."""
import pytest
from students.tests.factories import StudentFactory, FacultyFactory


@pytest.mark.django_db
def test_list_students_as_admin(authed_admin_client):
    StudentFactory()
    response = authed_admin_client.get('/api/students/')
    assert response.status_code == 200
    assert 'results' in response.data  # paginated


@pytest.mark.django_db
def test_list_faculties(authed_admin_client):
    FacultyFactory()
    response = authed_admin_client.get('/api/faculties/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_create_student(api_client):
    """Write operations require auth even on IsAuthenticatedOrReadOnly views."""
    response = api_client.post('/api/students/', {})
    assert response.status_code in [401, 403]
