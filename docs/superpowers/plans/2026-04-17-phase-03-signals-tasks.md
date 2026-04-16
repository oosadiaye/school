# Phase 3: Backend Signals & Tasks — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. TDD per task.

**Goal:** Wire Django signals for automation (notifications on key events, session deactivation, leave balance deduction) and add Celery Beat periodic tasks for scheduled operations (overdue checks, payment reminders, reservation expiry). Upgrade the existing email/SMS shells from Phase 2 to actually queue messages.

**Architecture:** Each app gets a `signals.py` (connected via AppConfig.ready()) and a `tasks.py` for async work. Signals call notification services synchronously for in-app notifications and defer email/SMS to Celery tasks. Celery Beat runs scheduled tasks on cron intervals.

**Tech Stack:** Django signals, Celery Beat, Redis broker (from Phase 1)

**Spec Reference:** `docs/superpowers/specs/2026-04-02-tims-production-readiness-design.md` §3.3, §3.4

---

## Pre-existing State

- `students/signals.py` already exists — auto-creates invoices on student creation. Needs refactoring to use InvoiceService instead of raw ORM.
- `core/tasks.py` has a `ping` task (Phase 1 sanity check).
- Only `students/apps.py` has a `ready()` method importing signals.
- Email/SMS service shells exist in `notifications/services.py` (Phase 2).

---

## Tasks

### Task 1: Refactor existing student signal + add welcome notification

**Files:**
- Modify: `backend/students/signals.py` — use InvoiceService, add notification
- Modify: `backend/students/apps.py` — verify ready() imports signals
- Create: `backend/students/tests/test_signals.py`

**Signal logic:**
```python
@receiver(post_save, sender=Student)
def on_student_created(sender, instance, created, **kwargs):
    if not created:
        return
    # 1. Generate invoices via service (replaces raw ORM)
    InvoiceService.generate_for_student(instance, session, by=None)
    # 2. Create welcome notification
    NotificationService.create(
        user=instance.user,
        level='success',
        title='Welcome to TIMS',
        message=f'Your registration is complete. Matric number: {instance.matric_number}',
    )
```

**Tests (3):**
- `test_student_creation_generates_invoices`
- `test_student_creation_creates_welcome_notification`
- `test_student_update_does_not_trigger_signal` (created=False guard)

**Commit:** `feat(signals): refactor student creation signal to use services + add welcome notification`

---

### Task 2: Academic signals (result published, session activated)

**Files:**
- Create: `backend/academic/signals.py`
- Modify: `backend/academic/apps.py` — add ready() importing signals
- Create: `backend/academic/tests/test_signals.py`

**Signals:**

```python
@receiver(post_save, sender=Result)
def on_result_status_change(sender, instance, **kwargs):
    if instance.is_published:
        # Notify student
        NotificationService.create(
            user=instance.student.user,
            level='info',
            title='Result Published',
            message=f'Your result for {instance.course.name} has been published.',
        )

@receiver(post_save, sender=AcademicSession)
def on_session_activated(sender, instance, **kwargs):
    if instance.is_current:
        # Deactivate others (SessionService already handles this, but signal
        # provides a safety net for direct model saves bypassing the service)
        AcademicSession.objects.exclude(pk=instance.pk).filter(
            is_current=True
        ).update(is_current=False)
```

**Tests (3):**
- `test_result_published_creates_notification`
- `test_result_unpublished_does_not_notify`
- `test_session_activation_deactivates_others`

**Commit:** `feat(signals): add academic signals for result notification and session deactivation`

---

### Task 3: Finance signals (payment confirmed)

**Files:**
- Create: `backend/finance/signals.py`
- Modify: `backend/finance/apps.py` — add ready()
- Create: `backend/finance/tests/test_signals.py`

**Signal:**
```python
@receiver(post_save, sender=Payment)
def on_payment_confirmed(sender, instance, **kwargs):
    if instance.status == 'completed':
        # Notify student
        NotificationService.create(
            user=instance.student,
            level='success',
            title='Payment Confirmed',
            message=f'Payment of ₦{instance.amount:,.2f} confirmed for invoice #{instance.invoice.id}.',
        )
```

Note: The actual invoice reconciliation is already handled by `PaymentService.verify_and_reconcile()` in an atomic transaction. This signal only adds the notification layer.

**Tests (2):**
- `test_payment_completed_creates_notification`
- `test_pending_payment_does_not_notify`

**Commit:** `feat(signals): add finance signal for payment confirmation notification`

---

### Task 4: HR signal (leave approved → balance deduction)

**Files:**
- Create: `backend/hr/signals.py`
- Modify: `backend/hr/apps.py` — add ready()
- Create: `backend/hr/tests/test_signals.py`

**Signal:**
```python
@receiver(post_save, sender=LeaveRequest)
def on_leave_approved(sender, instance, **kwargs):
    if instance.status == 'approved':
        NotificationService.create(
            user=instance.employee.user,
            level='success',
            title='Leave Approved',
            message=f'Your {instance.leave_type.name} leave from {instance.start_date} to {instance.end_date} has been approved.',
        )
```

Note: Leave balance deduction is already handled by `LeaveService.approve_leave()`. Signal adds notification.

**Tests (2):**
- `test_leave_approved_creates_notification`
- `test_leave_pending_does_not_notify`

**Commit:** `feat(signals): add HR signal for leave approval notification`

---

### Task 5: Library + Hostel + NUC signals (lightweight)

**Files:**
- Create: `backend/library/signals.py`, `backend/hostel/signals.py`, `backend/nuc/signals.py`
- Modify: respective `apps.py` files
- Create: respective `tests/test_signals.py` files

**Library signal:**
```python
@receiver(post_save, sender=BookLoan)
def on_book_returned(sender, instance, **kwargs):
    if instance.status == 'returned' and instance.fine_amount > 0:
        NotificationService.create(
            user=instance.member.user,
            level='warning',
            title='Book Return — Fine Applied',
            message=f'Fine of ₦{instance.fine_amount:,.2f} applied for overdue return.',
        )
```

**Hostel signal:**
```python
@receiver(post_save, sender=HostelAssignment)
def on_room_assigned(sender, instance, created, **kwargs):
    if created:
        NotificationService.create(
            user=instance.student.user,
            level='success',
            title='Room Assigned',
            message=f'You have been assigned to {instance.room.hostel.name}, Room {instance.room.room_number}.',
        )
```

**NUC signal:** (accreditation expiry warning — handled by Celery task instead, so NUC signal is minimal or skipped)

**Tests (4):**
- `test_book_return_with_fine_notifies`
- `test_book_return_no_fine_no_notification`
- `test_room_assignment_notifies_student`
- `test_room_assignment_update_does_not_notify` (created=False)

**Commit:** `feat(signals): add library and hostel notification signals`

---

### Task 6: Celery tasks — Finance periodic jobs

**Files:**
- Create: `backend/finance/tasks.py`
- Create: `backend/finance/tests/test_tasks.py`

**Tasks:**
```python
@shared_task
def check_overdue_invoices():
    """Flag overdue invoices and create payment reminder notifications."""
    overdue = InvoiceService.list_overdue()
    count = 0
    for invoice in overdue:
        if invoice.status != 'overdue':
            invoice.status = 'overdue'
            invoice.save(update_fields=['status'])
        NotificationService.create(
            user=invoice.student.user,
            level='warning',
            title='Invoice Overdue',
            message=f'Your invoice #{invoice.id} of ₦{invoice.amount:,.2f} is overdue.',
        )
        count += 1
    return f'{count} overdue invoices processed'

@shared_task
def send_payment_reminders():
    """Send reminders for unpaid invoices due within 7 days."""
    # Similar pattern — find invoices due soon, create notifications
```

**Tests (2):**
- `test_check_overdue_invoices_flags_and_notifies`
- `test_send_payment_reminders_creates_notifications`

**Commit:** `feat(tasks): add finance periodic tasks for overdue checks and payment reminders`

---

### Task 7: Celery tasks — Library + NUC periodic jobs

**Files:**
- Create: `backend/library/tasks.py`, `backend/nuc/tasks.py`
- Create: `backend/library/tests/test_tasks.py`, `backend/nuc/tests/test_tasks.py`

**Library tasks:**
```python
@shared_task
def check_overdue_books():
    """Flag overdue book loans and notify members."""
    overdue_loans = LoanService.list_overdue()
    for loan in overdue_loans:
        fine = LoanService.calculate_overdue_fine(loan)
        NotificationService.create(...)
    return f'{overdue_loans.count()} overdue loans processed'

@shared_task
def expire_old_reservations():
    """Cancel reservations older than 48 hours."""
    count = ReservationService.expire_old(hours=48)
    return f'{count} reservations expired'
```

**NUC task:**
```python
@shared_task
def check_expiring_accreditations():
    """Alert about accreditations expiring within 90 days."""
    expiring = AccreditationService.list_expiring(within_days=90)
    # Create admin notifications for each
```

**Tests (3):**
- `test_check_overdue_books_notifies_members`
- `test_expire_old_reservations_marks_expired`
- `test_check_expiring_accreditations_creates_alerts`

**Commit:** `feat(tasks): add library and NUC periodic tasks`

---

### Task 8: Celery Beat schedule configuration

**Files:**
- Modify: `backend/school/settings/base.py` — add CELERY_BEAT_SCHEDULE

**Schedule:**
```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-overdue-invoices': {
        'task': 'finance.tasks.check_overdue_invoices',
        'schedule': crontab(hour=8, minute=0),
    },
    'send-payment-reminders': {
        'task': 'finance.tasks.send_payment_reminders',
        'schedule': crontab(hour=9, minute=0, day_of_week='mon'),
    },
    'check-overdue-books': {
        'task': 'library.tasks.check_overdue_books',
        'schedule': crontab(hour=7, minute=0),
    },
    'expire-reservations': {
        'task': 'library.tasks.expire_old_reservations',
        'schedule': crontab(hour='*/6'),
    },
    'accreditation-expiry-alerts': {
        'task': 'nuc.tasks.check_expiring_accreditations',
        'schedule': crontab(hour=8, minute=0, day_of_week='mon'),
    },
}
```

**Tests (1):**
- `test_celery_beat_schedule_is_valid` — verify all task paths resolve

**Commit:** `feat(celery): configure Celery Beat schedule for periodic tasks`

---

### Task 9: Email/SMS queue integration

**Files:**
- Modify: `backend/notifications/services.py` — upgrade EmailService.queue_email and SMSService.queue_sms to dispatch Celery tasks
- Create: `backend/notifications/tasks.py` — actual send tasks
- Create: `backend/notifications/tests/test_tasks.py`

**Tasks:**
```python
@shared_task
def send_email_task(to, subject, body_text, body_html=None):
    """Send a single email via Django's email backend."""
    from django.core.mail import send_mail
    send_mail(subject, body_text, settings.DEFAULT_FROM_EMAIL, [to], html_message=body_html)

@shared_task
def send_sms_task(to_phone, message):
    """Send SMS via configured provider (Termii/Africa's Talking)."""
    # Placeholder — logs the message for now
    # Phase 10 will add real SMS gateway integration
    logger.info(f"SMS to {to_phone}: {message}")
```

**Update EmailService.queue_email:**
```python
@staticmethod
def queue_email(to, template_name, context):
    subject, body = EmailService.render_template(template_name, context)
    send_email_task.delay(to, subject, body)
```

**Tests (2):**
- `test_send_email_task_calls_django_send_mail` (mock send_mail)
- `test_queue_email_dispatches_celery_task` (mock .delay)

**Commit:** `feat(notifications): wire email/SMS sending via Celery tasks`

---

### Task 10: HR attendance summary task + Phase 3 verification

**Files:**
- Create: `backend/hr/tasks.py`
- Modify: `backend/school/settings/base.py` — add HR task to beat schedule
- Verify everything

**HR Task:**
```python
@shared_task
def daily_attendance_summary():
    """Generate daily attendance summary for all departments."""
    # Placeholder for daily attendance email to HODs
    logger.info("Daily attendance summary generated")
```

**Verification:**
- `pytest -v` → all tests pass (except Redis health check)
- `python manage.py check`
- All signals registered (check AppConfig.ready methods)
- All tasks discoverable by Celery (check `app.tasks` registry)
- Push + tag

**Commits:**
- `feat(tasks): add HR daily attendance summary task`
- `docs: mark Phase 3 complete in master plan`

---

## Execution Order

```
T1 (Refactor student signal) →
T2 (Academic signals) →
T3 (Finance signal) →
T4 (HR signal) →
T5 (Library + Hostel signals) →
T6 (Finance Celery tasks) →
T7 (Library + NUC Celery tasks) →
T8 (Beat schedule) →
T9 (Email/SMS queue) →
T10 (HR task + verification + push)
```

## Phase 3 Acceptance Criteria

- ✅ 6+ signals registered across apps (student, academic, finance, HR, library, hostel)
- ✅ 5+ Celery tasks (overdue invoices, payment reminders, overdue books, expire reservations, accreditation alerts)
- ✅ Celery Beat schedule configured with cron intervals
- ✅ Email service dispatches via Celery (not blocking request thread)
- ✅ 20+ new tests, all passing
- ✅ Existing signal refactored to use InvoiceService
- ✅ All tasks discoverable by Celery autodiscover
- ✅ `phase-3-signals-tasks` tag pushed to GitHub
