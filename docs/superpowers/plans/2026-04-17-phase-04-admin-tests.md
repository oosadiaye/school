# Phase 4: Backend Admin & Integration Tests — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. TDD where applicable.

**Goal:** Register all 46 models across 9 apps in Django admin with proper `list_display`, `list_filter`, `search_fields`, and `readonly_fields`. Then add integration tests for key API endpoints to verify the full request → view → service → model → response pipeline.

**Architecture:** Django admin registrations use `@admin.register(Model)` decorator pattern with `ModelAdmin` subclasses. Integration tests use the DRF `APIClient` and test real HTTP endpoints (unlike Phase 2's unit tests which tested services directly).

**Tech Stack:** Django admin, pytest-django, DRF APIClient

**Spec Reference:** `docs/superpowers/specs/2026-04-02-tims-production-readiness-design.md` §3.6

---

## Pre-existing State

- All 9 `admin.py` files are empty stubs (`# Register your models here.`)
- 46 models across 9 apps need registration
- 185 tests exist (all service + signal + task tests from Phases 1-3)
- No integration/view-level tests exist yet
- Factories exist for all apps (created in Phase 2)

---

## Tasks

### Task 1: Admin registrations — accounts + students + academic

**Files to modify:**
- `backend/accounts/admin.py`
- `backend/students/admin.py`
- `backend/academic/admin.py`

**accounts/admin.py** (2 models):
```python
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'created_at')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at')
    readonly_fields = ('created_at',)
```

**students/admin.py** (4 models): Faculty, Department, Programme, Student with appropriate fields

**academic/admin.py** (8 models): AcademicSession, Semester, Course, CourseAllocation, CourseRegistration, Attendance, Result, ExamSitting

Each model admin should have sensible `list_display` (3-6 fields), `list_filter` (status/type fields), `search_fields` (name/code fields), `readonly_fields` (timestamps).

**Tests:** Verify admin pages load:
```python
@pytest.mark.django_db
def test_admin_pages_load(admin_client):
    """Every registered model's admin changelist page returns 200."""
    from django.urls import reverse
    models = ['accounts_user', 'students_faculty', 'students_student', ...]
    for model in models:
        url = reverse(f'admin:{model}_changelist')
        response = admin_client.get(url)
        assert response.status_code == 200, f"Admin page for {model} failed"
```

**Commit:** `feat(admin): register accounts, students, academic models in Django admin`

---

### Task 2: Admin registrations — finance + library

**Files:** `backend/finance/admin.py`, `backend/library/admin.py`

**finance/admin.py** (10 models): FeeType, FeeStructure, InstallmentPlan, InstallmentPayment, FeeWaiver, Invoice, Payment, Scholarship, StudentScholarship, PaymentReminder

Finance admin should include:
- Invoice: `list_display` = student, fee_structure, amount, balance, status, due_date
- Payment: `list_display` = student, invoice, amount, status, payment_method, payment_date
- FeeWaiver: `list_display` = student, invoice, waiver_type, amount, is_approved

**library/admin.py** (6 models): Author, Category, Book, LibraryMember, BookLoan, Reservation

**Commit:** `feat(admin): register finance and library models in Django admin`

---

### Task 3: Admin registrations — hostel + hr + nuc + notifications

**Files:** `backend/hostel/admin.py`, `backend/hr/admin.py`, `backend/nuc/admin.py`, `backend/notifications/admin.py`

**hostel/admin.py** (5 models): Hostel, Room, HostelAssignment, HostelFee, RoomChangeRequest
**hr/admin.py** (6 models): Department, Employee, LeaveType, LeaveRequest, Attendance, Payroll
**nuc/admin.py** (5 models): Accreditation, NUCReport, ComplianceChecklist, ComplianceItem, GraduationList
**notifications/admin.py** (4 models): Notification, EmailTemplate, SMSTemplate, Announcement

**Commit:** `feat(admin): register hostel, HR, NUC, notifications models in Django admin`

---

### Task 4: Admin smoke tests

**Files:**
- Create: `backend/core/tests/test_admin.py`

Test that ALL admin changelist pages load without errors. Use `admin_client` fixture (from pytest-django — auto-creates admin user and logs into admin).

```python
import pytest
from django.urls import reverse
from django.apps import apps

ADMIN_MODELS = [
    'accounts_user', 'accounts_passwordreset',
    'students_faculty', 'students_department', 'students_programme', 'students_student',
    'academic_academicsession', 'academic_semester', 'academic_course',
    'academic_courseallocation', 'academic_courseregistration',
    'academic_attendance', 'academic_result', 'academic_examsitting',
    'finance_feetype', 'finance_feestructure', 'finance_invoice', 'finance_payment',
    'finance_installmentplan', 'finance_installmentpayment',
    'finance_feewaiver', 'finance_scholarship', 'finance_studentscholarship',
    'finance_paymentreminder',
    'library_author', 'library_category', 'library_book',
    'library_librarymember', 'library_bookloan', 'library_reservation',
    'hostel_hostel', 'hostel_room', 'hostel_hostelassignment',
    'hostel_hostelfee', 'hostel_roomchangerequest',
    'hr_department', 'hr_employee', 'hr_leavetype', 'hr_leaverequest',
    'hr_attendance', 'hr_payroll',
    'nuc_accreditation', 'nuc_nucreport', 'nuc_compliancechecklist',
    'nuc_complianceitem', 'nuc_graduationlist',
    'notifications_notification', 'notifications_emailtemplate',
    'notifications_smstemplate', 'notifications_announcement',
]

@pytest.mark.django_db
@pytest.mark.parametrize('model_name', ADMIN_MODELS)
def test_admin_changelist_loads(admin_client, model_name):
    url = reverse(f'admin:{model_name}_changelist')
    response = admin_client.get(url)
    assert response.status_code == 200, f"Admin changelist for {model_name} returned {response.status_code}"
```

This creates ~46 parametrized tests — one per model.

**Commit:** `test(admin): add parametrized admin changelist smoke tests for all 46 models`

---

### Task 5: Integration tests — auth endpoints

**Files:**
- Create: `backend/accounts/tests/test_views.py`

Test the actual HTTP endpoints:
```python
@pytest.mark.django_db
def test_login_endpoint_returns_tokens(api_client):
    user = UserFactory(username='loginview')
    response = api_client.post('/api/accounts/auth/login/', {
        'username': 'loginview', 'password': 'TestPass12345!'
    })
    assert response.status_code == 200
    assert 'access_token' in response.data

@pytest.mark.django_db
def test_login_endpoint_rejects_wrong_password(api_client):
    UserFactory(username='badlogin')
    response = api_client.post('/api/accounts/auth/login/', {
        'username': 'badlogin', 'password': 'WRONG'
    })
    assert response.status_code == 401
    assert response.data['error'] == 'invalid_credentials'

@pytest.mark.django_db
def test_me_endpoint_requires_auth(api_client):
    response = api_client.get('/api/accounts/users/me/')
    assert response.status_code == 401

@pytest.mark.django_db
def test_me_endpoint_returns_profile(authed_admin_client):
    response = authed_admin_client.get('/api/accounts/users/me/')
    assert response.status_code == 200
    assert 'username' in response.data

@pytest.mark.django_db
def test_change_password_via_endpoint(authed_admin_client, admin_user):
    response = authed_admin_client.post('/api/accounts/users/change_password/', {
        'old_password': 'TestPass12345!',
        'new_password': 'NewValidPass12!',
    })
    assert response.status_code == 200
```

**Commit:** `test(integration): add auth endpoint integration tests`

---

### Task 6: Integration tests — student + academic endpoints

**Files:**
- Create: `backend/students/tests/test_views.py`
- Create: `backend/academic/tests/test_views.py`

Student tests:
- `test_list_students_as_admin` — GET /api/students/ → 200 with paginated results
- `test_create_student` — POST → 201
- `test_student_sees_own_profile` — GET /api/students/my_profile/ → 200
- `test_update_student_status` — POST /api/students/{id}/update_status/ → 200

Academic tests:
- `test_register_courses` — POST /api/academic/course-registrations/register_courses/ → 200
- `test_get_my_results` — GET /api/academic/results/my_results/ → 200
- `test_calculate_gpa` — GET /api/academic/results/calculate_gpa/ → 200
- `test_current_session` — GET /api/academic/sessions/current/ → 200

**Commit:** `test(integration): add student and academic endpoint tests`

---

### Task 7: Integration tests — finance endpoints

**Files:**
- Create: `backend/finance/tests/test_views.py`

Finance tests:
- `test_generate_invoices_as_admin` — POST → 200
- `test_my_invoices_as_student` — GET → 200
- `test_overdue_invoices_as_admin` — GET → 200
- `test_finance_dashboard` — GET → 200
- `test_waivers_report` — GET → 200 (regression for Phase 1 bug fix)
- `test_payment_initiation` — POST (may need gateway mock)
- `test_non_admin_cannot_generate_invoices` — 403

**Commit:** `test(integration): add finance endpoint integration tests`

---

### Task 8: Integration tests — remaining apps + Phase 4 verification

**Files:**
- Create: `backend/library/tests/test_views.py`
- Create: `backend/hostel/tests/test_views.py`
- Create: `backend/hr/tests/test_views.py`
- Create: `backend/notifications/tests/test_views.py`

Basic CRUD endpoint tests for each (2-3 per app):
- List endpoint returns 200 for authed user
- Create endpoint returns 201
- Unauthorized returns 401

**Phase 4 Verification:**
- `pytest -v` — all pass (expect 230+)
- `python manage.py check`
- Frontend build
- Push + tag `phase-4-admin-tests`
- Update master plan

**Commits:**
- `test(integration): add remaining app endpoint tests`
- `docs: mark Phase 4 complete in master plan`

---

## Phase 4 Acceptance Criteria

- ✅ All 46 models registered in Django admin
- ✅ Admin changelist smoke tests (46 parametrized tests)
- ✅ Integration tests for all key endpoints (~30+ new tests)
- ✅ Total test count: 230+
- ✅ `phase-4-admin-tests` tag on GitHub
