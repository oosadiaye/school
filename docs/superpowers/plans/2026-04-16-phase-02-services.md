# Phase 2: Backend Service Layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Each task follows TDD: write failing test → verify RED → implement → verify GREEN → commit.

**Goal:** Extract business logic from all 9 Django app views into dedicated `services.py` modules with unit test coverage, implement a custom DRF exception handler for standardized error responses, and tighten serializer validation.

**Architecture:** Each app gets a `services.py` containing one or more service classes (e.g., `InvoiceService`, `PaymentService`). Views become thin HTTP adapters: parse input → call service → serialize result. Services are stateless, `@staticmethod` where possible, and DB transactions are explicit via `transaction.atomic` context managers.

**Tech Stack:** Django 4.2, DRF 3.14, pytest-django, factory_boy (added in Phase 1).

**Spec Reference:** `docs/superpowers/specs/2026-04-02-tims-production-readiness-design.md` §3

---

## File Map

**Create (per app):**
- `backend/<app>/services.py` — service classes with business logic
- `backend/<app>/exceptions.py` — app-specific domain exceptions
- `backend/<app>/tests/test_services.py` — unit tests for service methods
- `backend/<app>/tests/factories.py` — factory_boy factories for app models

**Create (cross-cutting):**
- `backend/core/exceptions.py` — base exception classes + DRF exception handler

**Modify (per app):**
- `backend/<app>/views.py` — thin adapters calling services
- `backend/<app>/serializers.py` — field + cross-field validation

**Modify (project):**
- `backend/school/settings/base.py` — register custom EXCEPTION_HANDLER

---

## Inventory of Thick Methods Being Extracted

From the audit of all 9 apps (concentrated in academic + finance):

| Method | Lines | → Extracts to |
|--------|-------|---------------|
| `academic.register_courses()` | 47 | `RegistrationService.register_courses_bulk()` |
| `academic.generate_seating()` | 48 | `ExamSittingService.generate_seating_for_course()` |
| `academic.calculate_gpa()` | 34 | `ResultService.calculate_gpa_cgpa()` |
| `finance.generate_invoices()` | 47 | `InvoiceService.generate_bulk()` |
| `finance.generate_for_student()` | 35 | `InvoiceService.generate_for_student()` |
| `finance.create_installments_bulk()` | 21 | `InvoiceService.create_installments()` |
| `finance.initiate_payment()` | 45 | `PaymentService.initiate()` |
| `finance.verify_payment()` | 48 | `PaymentService.verify_and_reconcile()` |
| `finance.approve()` (FeeWaiver) | 23 | `FeeWaiverService.approve_waiver()` |
| `finance.summary()` | 42 | `FinanceReportService.summary()` |
| `finance.payment_trends()` | 22 | `FinanceReportService.payment_trends()` |

The remaining 4 apps (library, hostel, hr, nuc) have mostly vanilla CRUD — services created for consistency and to host business rules added in later phases.

---

## Tasks

### Task 1: Foundation — Custom DRF Exception Handler + BaseService Pattern

**Files:**
- Create: `backend/core/exceptions.py`
- Create: `backend/core/tests/test_exceptions.py`
- Modify: `backend/school/settings/base.py` — add EXCEPTION_HANDLER
- Create: `backend/core/services.py` — BaseService conventions (docs-only class for now)

**Why:** Every service error needs consistent JSON format `{"error": code, "message": str, "details": dict}`. DRF's default handler is inconsistent between DRF exceptions and Python exceptions. Custom handler unifies them.

**Service Pattern** (documented in `core/services.py`):
```python
class BaseService:
    """All services are stateless. Use @staticmethod or @classmethod.
    Raise DomainError subclasses for business-rule violations.
    Wrap multi-step DB operations with transaction.atomic."""
```

**Custom Exception Classes** (core/exceptions.py):
- `DomainError(Exception)` — base for all business-rule violations
- `ValidationFailed(DomainError)` — validation errors → HTTP 400
- `PermissionDenied(DomainError)` — authz errors → HTTP 403
- `NotFound(DomainError)` — resource missing → HTTP 404
- `ConflictError(DomainError)` — state conflicts → HTTP 409

**TDD Tests:**
- `test_validation_failed_returns_400_with_standard_json`
- `test_conflict_error_returns_409`
- `test_drf_default_exceptions_still_work`
- `test_unhandled_exception_returns_500_with_safe_message`

**Acceptance:**
- `EXCEPTION_HANDLER` registered in REST_FRAMEWORK config
- All 4 exception tests pass
- Existing endpoints still behave correctly (no regression)

**Commit:** `feat(core): add custom DRF exception handler and domain error hierarchy`

---

### Task 2: Accounts — AuthService + UserService

**Files:**
- Create: `backend/accounts/services.py`
- Create: `backend/accounts/exceptions.py`
- Create: `backend/accounts/tests/factories.py` (UserFactory)
- Create: `backend/accounts/tests/test_services.py`
- Modify: `backend/accounts/views.py` — use AuthService, UserService

**Services:**

**`AuthService`:**
- `login(username, password) -> dict` — validate credentials, return access/refresh tokens + user payload. Raises `InvalidCredentials` on failure.
- `refresh_access_token(refresh_token) -> str` — decode refresh token, return new access token. Raises `InvalidToken` on expiry/tampering.
- `change_password(user, old_password, new_password)` — verify old, validate new via Django validators, save. Raises `InvalidCredentials`.

**`UserService`:**
- `create_user(data, created_by)` — create user with role validation
- `update_user(user, data, updated_by)` — enforce role changes require admin
- `deactivate_user(user, by)` — soft-delete (set is_active=False)

**Domain Exceptions:** `InvalidCredentials`, `InvalidToken`, `AccountDisabled`

**Tests:**
- `test_login_returns_tokens_for_valid_credentials`
- `test_login_raises_invalid_credentials_on_wrong_password`
- `test_login_raises_account_disabled_when_inactive`
- `test_refresh_access_token_returns_new_token`
- `test_refresh_raises_invalid_token_on_expired`
- `test_change_password_verifies_old_password`
- `test_change_password_enforces_validators`
- `test_create_user_assigns_correct_role`

**Acceptance:** All 8 tests pass + views refactored to call AuthService/UserService.

**Commit:** `refactor(accounts): extract business logic to AuthService and UserService`

---

### Task 3: Students — StudentService + FacultyService + DepartmentService + ProgrammeService

**Files:**
- Create: `backend/students/services.py`
- Create: `backend/students/exceptions.py`
- Create: `backend/students/tests/__init__.py`, `factories.py`, `test_services.py`
- Delete: `backend/students/tests.py` (if boilerplate)
- Modify: `backend/students/views.py`

**Services:**

**`StudentService`:**
- `generate_matric_number(programme, session) -> str` — extract existing auto-gen logic from model, make testable
- `update_status(student, new_status, by) -> Student` — validate transition, log change. Raises `InvalidStatusTransition`.
- `filter_visible_to(user) -> QuerySet[Student]` — apply role-based filtering
- `get_student_profile_for(user) -> Student` — student's own or raises `NotFound`

**`FacultyService`, `DepartmentService`, `ProgrammeService`:**
- `delete_if_empty(faculty, by)` — raises `HasActiveRecords` if programmes/students linked
- Validation helpers

**Tests:**
- `test_matric_number_is_unique_per_programme_and_session`
- `test_update_status_allows_active_to_suspended`
- `test_update_status_blocks_graduated_to_active`
- `test_filter_visible_to_returns_only_own_record_for_student`
- `test_filter_visible_to_returns_all_for_admin`
- `test_delete_faculty_with_active_students_raises_has_active_records`

**Commit:** `refactor(students): extract student lifecycle and cascade validation to services`

---

### Task 4: Academic — RegistrationService (THICK)

**Files:**
- Create: `backend/academic/services.py` (start — more classes added in Task 5, 6)
- Create: `backend/academic/exceptions.py`
- Create: `backend/academic/tests/__init__.py`, `factories.py`, `test_services.py`
- Modify: `backend/academic/views.py` — replace `register_courses` body

**Service:**

**`RegistrationService`:**
- `register_courses_bulk(student, course_ids, semester) -> dict` — replaces the 47-line view method
  - Verify session is_registration_open (raises `RegistrationClosed`)
  - Fetch courses, check all exist (raises `CourseNotFound` with list)
  - Check each course allocation for semester
  - De-duplicate against existing registrations
  - Bulk create CourseRegistration records in transaction
  - Returns `{"registered": [ids], "skipped_duplicates": [ids], "total_credits": int}`

**Domain Exceptions:** `RegistrationClosed`, `CourseNotFound`, `CreditOverload` (for future phase)

**Tests:**
- `test_register_courses_bulk_creates_registrations`
- `test_register_courses_bulk_raises_when_registration_closed`
- `test_register_courses_bulk_skips_duplicates`
- `test_register_courses_bulk_raises_when_course_not_found`
- `test_register_courses_bulk_wraps_in_transaction` (partial failure rolls back)

**Commit:** `refactor(academic): extract course registration to RegistrationService`

---

### Task 5: Academic — ResultService + SessionService + SemesterService

**Files:** Extend `backend/academic/services.py`, add tests

**Services:**

**`ResultService`:**
- `calculate_gpa_cgpa(student, semester=None) -> dict` — replaces 34-line view method; weighted formula `sum(grade_point * credit_units) / sum(credit_units)`
- `publish_result(result, by) -> Result` — state transition draft → published, triggers notification
- `get_student_results(student, semester=None) -> QuerySet[Result]` — filtered accessor

**`SessionService`:**
- `activate_session(session, by) -> AcademicSession` — deactivates previous in transaction
- `get_current() -> AcademicSession | None` — cached

**`SemesterService`:**
- `get_active() -> Semester | None`

**Tests:**
- `test_calculate_gpa_with_single_result`
- `test_calculate_gpa_with_mixed_grades`
- `test_calculate_gpa_returns_zero_when_no_results`
- `test_calculate_cgpa_aggregates_across_semesters`
- `test_publish_result_updates_status`
- `test_publish_result_raises_if_already_published`
- `test_activate_session_deactivates_previous`

**Commit:** `refactor(academic): add ResultService with GPA calculation and SessionService`

---

### Task 6: Academic — CourseService + AttendanceService + ExamSittingService

**Files:** Extend `backend/academic/services.py`, add tests

**Services:**

**`CourseService`:**
- `delete_if_no_registrations(course, by)` — cascade protection
- `allocate_to_lecturer(course, lecturer, session, by) -> CourseAllocation`

**`AttendanceService`:**
- `mark_attendance(student, course, date, status, marked_by) -> Attendance`
- `get_course_attendance_summary(course, semester) -> dict` — per-student percentages

**`ExamSittingService`:**
- `generate_seating_for_course(course, hall, seat_prefix) -> list[ExamSitting]` — replaces 48-line view method; handles dedup, seat numbering `f"{idx + 1:03d}"`

**Tests:**
- `test_delete_course_with_registrations_raises`
- `test_mark_attendance_creates_record`
- `test_mark_attendance_updates_existing_same_day`
- `test_attendance_summary_calculates_percentages`
- `test_generate_seating_assigns_sequential_seats`
- `test_generate_seating_skips_students_already_seated`

**Commit:** `refactor(academic): add CourseService, AttendanceService, ExamSittingService`

---

### Task 7: Finance — InvoiceService (THICK)

**Files:**
- Create: `backend/finance/services.py`
- Create: `backend/finance/exceptions.py`
- Extend: `backend/finance/tests/` (factories.py, test_services.py)
- Modify: `backend/finance/views.py` — use InvoiceService

**Service:**

**`InvoiceService`:**
- `generate_bulk(session, level=None, programme=None, by) -> dict` — replaces 47-line view method
  - Look up FeeStructure entries matching filters
  - For each student matching filters (without existing invoice), create invoice
  - Trigger installment creation if plan exists
  - Returns `{"created": int, "skipped": int, "errors": []}`
- `generate_for_student(student, session, by) -> list[Invoice]` — replaces 35-line view method
- `create_installments(plan, num_installments) -> list[InstallmentPayment]` — replaces 21-line method; divides amount, 30-day intervals
- `list_overdue(as_of=None) -> QuerySet[Invoice]` — filter and annotate days_overdue
- `get_visible_to(user) -> QuerySet[Invoice]`

**Domain Exceptions:** `InvoiceExists`, `NoFeeStructureFound`

**Tests:**
- `test_generate_bulk_creates_invoices_for_all_matching_students`
- `test_generate_bulk_skips_existing_invoices`
- `test_generate_bulk_rolls_back_on_error`
- `test_generate_for_student_creates_invoice_per_fee_structure`
- `test_create_installments_divides_amount_evenly`
- `test_create_installments_spreads_due_dates_by_30_days`
- `test_list_overdue_excludes_paid_invoices`

**Commit:** `refactor(finance): extract invoice generation logic to InvoiceService`

---

### Task 8: Finance — PaymentService (THICK, CRITICAL)

**Files:** Extend `backend/finance/services.py`

**Service:**

**`PaymentService`:**
- `initiate(invoice, provider, user_email, callback_url) -> dict` — replaces 45-line view method
  - Validate provider in `['paystack', 'flutterwave', 'stripe']` (raises `InvalidPaymentProvider`)
  - Create Payment record with status='pending'
  - Call gateway via `payment_gateway.PaymentGateway.initialize(...)` — this is the existing wrapper
  - Return `{"payment_id", "gateway_reference", "authorization_url"}` or `{"error"}` if gateway failed
- `verify_and_reconcile(gateway_reference) -> Payment` — replaces 48-line view method
  - Look up Payment by gateway_reference
  - Call gateway.verify() — raises `PaymentVerificationFailed` if gateway says no
  - In `transaction.atomic`:
    - Update Payment status='success', paid_at=now
    - Reduce Invoice.balance by payment.amount
    - Mark Invoice.status='paid' if balance == 0
    - If linked to InstallmentPayment, mark installment as paid
- `get_visible_to(user) -> QuerySet[Payment]`

**Domain Exceptions:** `InvalidPaymentProvider`, `PaymentInitiationFailed`, `PaymentVerificationFailed`, `PaymentAlreadyVerified`

**Tests (use `responses` to mock gateway):**
- `test_initiate_creates_pending_payment`
- `test_initiate_calls_gateway_with_correct_params`
- `test_initiate_raises_on_invalid_provider`
- `test_initiate_returns_error_when_gateway_fails`
- `test_verify_and_reconcile_updates_payment_and_invoice`
- `test_verify_and_reconcile_rolls_back_on_error`
- `test_verify_and_reconcile_is_idempotent` (second call noop)
- `test_verify_raises_when_gateway_says_failed`
- `test_partial_payment_reduces_balance_without_marking_paid`

**Commit:** `refactor(finance): extract payment initiation and reconciliation to PaymentService`

---

### Task 9: Finance — FeeWaiverService + ScholarshipService + InstallmentPlanService

**Files:** Extend `backend/finance/services.py`

**Services:**

**`FeeWaiverService`:**
- `request_waiver(student, invoice, waiver_type, amount_or_percent, reason, by) -> FeeWaiver`
- `approve_waiver(waiver, approved_by) -> FeeWaiver` — replaces 23-line view method
  - Calculate reduction: `full` / `partial` (amount) / `percentage`
  - Update invoice balance in transaction
  - Set waiver.is_approved=True, approved_at=now, approved_by
- `reject_waiver(waiver, reason, by)`

**`ScholarshipService`:**
- `assign_scholarship(student, scholarship, session, by) -> StudentScholarship`
- `apply_to_invoice(student_scholarship, invoice)` — deduct scholarship from invoice

**`InstallmentPlanService`:**
- `get_plan_installments(plan) -> QuerySet[InstallmentPayment]`

**Tests:**
- `test_approve_full_waiver_zeros_invoice_balance`
- `test_approve_partial_waiver_reduces_balance`
- `test_approve_percentage_waiver_calculates_correctly`
- `test_approve_waiver_is_transactional`
- `test_reject_waiver_sets_status_without_affecting_balance`
- `test_scholarship_applies_to_invoice`

**Commit:** `refactor(finance): extract waiver approval and scholarship logic to services`

---

### Task 10: Finance — FinanceReportService + Views Refactor Wrap-Up

**Files:** Extend `backend/finance/services.py`, complete `backend/finance/views.py` refactor

**Service:**

**`FinanceReportService`:**
- `summary() -> dict` — replaces 42-line view method; aggregates total billed/paid/outstanding/waived/collection_rate
- `by_programme() -> list[dict]`
- `by_level() -> list[dict]`
- `payment_trends(days=30) -> list[dict]` — replaces 22-line method; time-series
- `waivers_report() -> dict` (reuse Phase 1 fix)

**Tests:**
- `test_summary_returns_correct_totals`
- `test_summary_handles_empty_database`
- `test_by_programme_groups_correctly`
- `test_payment_trends_covers_requested_days`
- `test_payment_trends_defaults_to_30_days`

**Views refactor:** Every action in `finance/views.py` now ≤ 15 lines and calls a service method.

**Commit:** `refactor(finance): complete service layer extraction; views are thin adapters`

---

### Task 11: Library — BookService + LoanService + ReservationService

**Files:**
- Create: `backend/library/services.py`, `exceptions.py`
- Create: `backend/library/tests/__init__.py`, `factories.py`, `test_services.py`
- Modify: `backend/library/views.py`

**Services:**

**`BookService`:**
- `create_book(data, by) -> Book` — with inventory init (copies_total, copies_available)
- `update_availability(book, delta)` — atomic adjust available copies

**`LoanService`:**
- `borrow(member, book, due_date=None, by) -> BookLoan` — validates book available, decrements `copies_available`, defaults due_date to 14 days. Raises `BookUnavailable`.
- `return_loan(loan, returned_on=None, by) -> BookLoan` — calculates fine (₦50/day overdue), updates availability, sets returned_at
- `calculate_overdue_fine(loan, as_of=None) -> Decimal` — per-day fine
- `list_overdue_loans() -> QuerySet[BookLoan]`

**`ReservationService`:**
- `reserve_book(member, book, by) -> Reservation` — raises `AlreadyReserved` if active exists
- `cancel_reservation(reservation, by)`
- `expire_old_reservations(hours=48) -> int` — called by Celery task in Phase 3

**Domain Exceptions:** `BookUnavailable`, `LoanNotActive`, `AlreadyReserved`

**Tests:**
- `test_borrow_decrements_available_copies`
- `test_borrow_raises_when_no_copies_available`
- `test_borrow_sets_default_14_day_due_date`
- `test_return_calculates_overdue_fine`
- `test_return_increments_available_copies`
- `test_reserve_book_creates_active_reservation`
- `test_reserve_raises_if_user_already_has_active_reservation`
- `test_expire_old_reservations_marks_expired_correctly`

**Commit:** `refactor(library): add BookService, LoanService, ReservationService with fine calculation`

---

### Task 12: Hostel — AllocationService + RoomChangeService + FeeService

**Files:**
- Create: `backend/hostel/services.py`, `exceptions.py`
- Create: `backend/hostel/tests/__init__.py`, `factories.py`, `test_services.py`
- Modify: `backend/hostel/views.py`

**Services:**

**`AllocationService`:**
- `assign_room(student, hostel, room, session, by) -> HostelAssignment` — validates:
  - Gender match (hostel.gender in ['mixed', student.gender])
  - Room has capacity (current_occupants < room.capacity)
  - No active allocation for student this session
  - Raises `GenderMismatch`, `RoomFull`, `AlreadyAllocated`
- `deallocate(assignment, reason, by)`
- `list_occupancy(hostel) -> dict` — room-level occupancy report

**`RoomChangeService`:**
- `request_room_change(assignment, desired_room, reason, by) -> RoomChangeRequest`
- `approve_room_change(request, by) -> HostelAssignment` — swap rooms transactionally

**`FeeService`:**
- `generate_hostel_fee(assignment, by) -> HostelFee`

**Domain Exceptions:** `GenderMismatch`, `RoomFull`, `AlreadyAllocated`

**Tests:**
- `test_assign_room_succeeds_when_capacity_available`
- `test_assign_room_raises_gender_mismatch`
- `test_assign_room_raises_room_full`
- `test_assign_room_raises_already_allocated`
- `test_deallocate_frees_capacity`
- `test_approve_room_change_swaps_assignments`

**Commit:** `refactor(hostel): add allocation and room change services with capacity enforcement`

---

### Task 13: HR — EmployeeService + LeaveService + PayrollService + AttendanceService

**Files:**
- Create: `backend/hr/services.py`, `exceptions.py`
- Create: `backend/hr/tests/__init__.py`, `factories.py`, `test_services.py`
- Modify: `backend/hr/views.py`

**Services:**

**`EmployeeService`:**
- `onboard(user, department, designation, by) -> Employee`
- `transfer_department(employee, new_department, by)`

**`LeaveService`:**
- `request_leave(employee, leave_type, start_date, end_date, reason) -> LeaveRequest`
  - Validate date range
  - Check leave balance (raises `InsufficientLeaveBalance`)
  - Default status='pending'
- `approve_leave(leave_request, by) -> LeaveRequest` — state transition + deduct from balance in transaction
- `reject_leave(leave_request, reason, by)`
- `get_leave_balance(employee, leave_type, year) -> int`

**`PayrollService`:**
- `generate_monthly_payroll(employee, month, year, by) -> Payroll` — calculates base + allowances - deductions (tax, pension)
- `generate_bulk_payroll(month, year, by) -> list[Payroll]`

**`AttendanceService`:**
- `check_in(employee, time=None) -> Attendance`
- `check_out(employee, time=None) -> Attendance`
- `monthly_summary(employee, month, year) -> dict`

**Domain Exceptions:** `InsufficientLeaveBalance`, `AlreadyCheckedIn`, `NotCheckedIn`

**Tests:**
- `test_request_leave_raises_on_insufficient_balance`
- `test_approve_leave_deducts_from_balance`
- `test_approve_leave_is_transactional`
- `test_reject_leave_does_not_affect_balance`
- `test_generate_monthly_payroll_calculates_net_correctly`
- `test_check_in_creates_attendance_record`
- `test_check_in_raises_if_already_checked_in_today`

**Commit:** `refactor(hr): add EmployeeService, LeaveService, PayrollService, AttendanceService`

---

### Task 14: NUC — AccreditationService + ComplianceService + NUCReportService

**Files:**
- Create: `backend/nuc/services.py`, `exceptions.py`
- Create: `backend/nuc/tests/__init__.py`, `factories.py`, `test_services.py`
- Modify: `backend/nuc/views.py`

**Services:**

**`AccreditationService`:**
- `record_accreditation(programme, status, valid_until, by) -> Accreditation`
- `list_expiring(within_days=90) -> QuerySet[Accreditation]` — for Celery alert task (Phase 3)

**`ComplianceService`:**
- `create_checklist(session, by) -> ComplianceChecklist`
- `update_item(item, is_completed, evidence, by)`
- `calculate_completion_percentage(checklist) -> float`

**`NUCReportService`:**
- `create_report(report_type, session, by) -> NUCReport`
- `generate_graduation_list(programme, session) -> list[dict]`

**Tests:**
- `test_record_accreditation_creates_entry`
- `test_list_expiring_returns_accreditations_within_window`
- `test_calculate_completion_returns_100_when_all_complete`
- `test_calculate_completion_returns_fraction_when_partial`
- `test_generate_graduation_list_returns_eligible_students`

**Commit:** `refactor(nuc): add AccreditationService, ComplianceService, NUCReportService`

---

### Task 15: Notifications — NotificationService + EmailService + SMSService shells

**Files:**
- Create: `backend/notifications/services.py`, `exceptions.py`
- Create: `backend/notifications/tests/__init__.py`, `factories.py`, `test_services.py`
- Modify: `backend/notifications/views.py`

**Services:**

**`NotificationService`:**
- `create(user, level, title, message, link=None) -> Notification`
- `create_for_audience(audience, ...)` — bulk create by user_type/department
- `mark_read(notification, user)` — authorization check
- `mark_all_read(user) -> int`
- `unread_count(user) -> int`

**`EmailService`** (shell for Phase 3 to add real sending):
- `render_template(template_name, context) -> tuple[subject, body_text, body_html]`
- `queue_email(to, template_name, context) -> EmailLog` — writes to log model, Phase 3 adds Celery task for actual send

**`SMSService`** (shell):
- `render_template(template_name, context) -> str`
- `queue_sms(to_phone, template_name, context) -> SMSLog`

**`AnnouncementService`:**
- `publish(title, body, audience, created_by) -> Announcement`
- `for_user(user) -> QuerySet[Announcement]` — filter by audience matching user.user_type

**Tests:**
- `test_create_notification_persists_record`
- `test_mark_read_only_works_for_owner`
- `test_mark_all_read_updates_all_unread`
- `test_unread_count_excludes_read`
- `test_create_for_audience_respects_user_type`
- `test_render_email_template_substitutes_context`
- `test_announcement_for_user_filters_by_audience`

**Commit:** `refactor(notifications): add NotificationService, EmailService/SMSService shells, AnnouncementService`

---

### Task 16: Serializer Tightening Pass

**Files:** Modify every `<app>/serializers.py`

**Validation additions:**

| Model / field | Validation |
|---------------|-----------|
| User.phone | Pattern: `^\+234\d{10}$` (optional if blank) |
| Student.date_of_birth | Must be in past, must make student >= 10 years old |
| CourseRegistration | Validate session+semester both active |
| Result.ca_score / exam_score | Both in range, sum ≤ 100 |
| Invoice.amount | > 0 |
| Payment.amount | > 0, must equal invoice.balance or less |
| LeaveRequest | end_date > start_date |
| HostelAssignment | student.gender matches hostel.gender (or hostel=mixed) |
| BookLoan.due_date | > loan_date |
| FeeWaiver.amount or percentage | exactly one set, amount > 0 or percentage 1-100 |
| Notification.link | Must be valid URL if set |

Use DRF `validators=` for field-level, override `validate()` for cross-field.

**Tests:** Add to each app's test_serializers.py (new file per app where needed):
- test_invalid_phone_format_rejected
- test_future_date_of_birth_rejected
- test_ca_exam_sum_over_100_rejected
- test_invoice_amount_zero_rejected
- test_leave_end_before_start_rejected
- test_fee_waiver_both_amount_and_percentage_rejected

**Commit:** `feat(validation): tighten serializer validation across all apps`

---

### Task 17: Custom Exception Handler Integration Verification

**Files:** None (verification task)

**Goals:**
- Every service raises `DomainError` subclasses, never bare `Exception`
- DRF exception handler catches them and returns `{"error": code, "message": str, "details": dict}` with correct HTTP status
- Verify: grep views.py for `try:` / `except:` — should be minimal now (services handle errors)

**Verification commands:**
```bash
cd backend
source venv/Scripts/activate
# Run every app's tests
pytest -v
# Check no raw 500 responses — all errors should route through handler
python manage.py check
```

**Manual checks:**
- Hit `/api/finance/payments/initiate_payment/` with invalid provider → expect 400 JSON, not 500
- Hit `/api/academic/course-registrations/register_courses/` when registration closed → expect 409 JSON
- Hit `/api/library/loans/` to borrow unavailable book → expect 409 JSON

**Commit:** No new commit if everything works. If fixes needed: `fix(errors): ensure all view-level exceptions route through custom handler`

---

### Task 18: Phase 2 Verification & Push

**Files:** Modify `docs/superpowers/plans/2026-04-16-master-plan.md` (mark Phase 2 complete)

**Checks:**
- [ ] `pytest -v` — all tests pass (aside from known Redis-environmental)
- [ ] Test count: Phase 1 had 8; Phase 2 should add ~60+ new tests (est. 70+ total)
- [ ] `python manage.py check` passes
- [ ] `python manage.py check --deploy` passes with env vars set
- [ ] `npm run build` succeeds in frontend (no backend-level change breaks frontend)
- [ ] `git status` clean
- [ ] Views grep: no view method > 20 lines (except where truly justified)
- [ ] Services grep: all service methods have docstrings

**Commands:**
```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git push origin main
git tag -a phase-2-services -m "Phase 2: Backend service layer extraction complete"
git push origin phase-2-services

# Update master plan Phase 2 row to ✅ Complete
# Commit and push
```

**Commit:** `docs: mark Phase 2 complete in master plan`

---

## Execution Order

Sequential (each task builds on prior test infrastructure):
```
T1 (Foundation) →
T2 (Accounts) →
T3 (Students) →
T4-T6 (Academic: Registration, Result/Session, Course/Attendance/Exam) →
T7-T10 (Finance: Invoice, Payment, Waiver/Scholarship, Reports) →
T11 (Library) →
T12 (Hostel) →
T13 (HR) →
T14 (NUC) →
T15 (Notifications) →
T16 (Serializer tightening) →
T17 (Exception handler verification) →
T18 (Phase 2 push + tag)
```

Tasks within the same app (T4-T6 or T7-T10) can technically parallelize if services.py merge cleanly, but serial execution is safer.

---

## Phase 2 Acceptance Criteria

After Phase 2 completes:
- ✅ All 9 apps have `services.py` with extracted business logic
- ✅ All services have unit tests (70%+ coverage on services)
- ✅ All views ≤ 20 lines per method (thin adapters)
- ✅ Custom DRF exception handler returns standardized JSON errors
- ✅ Tightened serializer validation across all apps
- ✅ `pytest -v` shows ~70+ tests, all passing (except Redis-environmental health)
- ✅ `git push origin main` succeeds with phase-2-services tag

---

## What's Still Deferred

- Django signals (`signals.py`) — Phase 3
- Celery tasks for real (payment reminders, overdue books, etc.) — Phase 3
- Admin UI registrations — Phase 4
- Integration/view-level tests — Phase 4
- Email/SMS actual sending — Phase 3 uses the shells added here
