# TIMS Production Readiness — Full Design Spec

**Date:** 2026-04-02
**Project:** Tertiary Institution Management System (TIMS)
**Approach:** Backend-First Rebuild with Full Modernization
**Deployment Target:** VPS (Nginx + Gunicorn + PostgreSQL)

---

## 1. Current State Summary

### Backend (Django REST Framework + PostgreSQL)
- **9 apps:** accounts, students, academic, finance, library, hostel, hr, nuc, notifications
- **Well-structured models** with proper relationships and auto-generated fields
- **JWT authentication** with Bearer tokens, refresh flow
- **API routes** via DRF ViewSets + Routers

**Critical issues:**
- Runtime bug in `finance/views.py` ~line 571: `total_waivered` should be `total_waived`
- All `admin.py` files are empty stubs — no Django admin registrations
- Zero test coverage — all 9 test files are boilerplate stubs
- Security: `DEBUG=True`, `CORS_ALLOW_ALL_ORIGINS=True`, hardcoded `SECRET_KEY`, exposed DB creds
- No `requirements.txt` — dependencies only in venv
- Email/SMS templates exist but no sending logic
- Payment gateway (`finance/payment_gateway.py`) has no error handling for network failures
- No background task processing (no Celery)
- No audit logging

### Frontend (React 19 + Vite + Axios)
- **17 pages**, glass morphism UI with custom components
- **4 pages completely stub** (Library, Hostel, HR, NUC) — hardcoded fake data
- `Library.jsx` calls wrong API (`studentService.getFaculties` instead of `libraryService.getBooks`)
- Finance Invoices/Payments tabs never fetch data
- Dashboard course progress, events, recent activity are hardcoded
- Settings saves nothing to backend
- Header search styled but non-functional
- Notification bell shows red dot but no functionality
- Faculties/Departments/Programmes forms don't call APIs
- Users page edit/delete buttons non-functional
- No TypeScript, no form validation library, no tests, no state management beyond Context

---

## 2. Foundation & Infrastructure

### 2.1 Environment Configuration
- **python-decouple** for all environment variables
- `.env` file with `.env.example` template checked into git
- Settings split:
  - `settings/base.py` — shared settings (installed apps, middleware, auth, REST framework config)
  - `settings/development.py` — `DEBUG=True`, `CORS_ALLOW_ALL_ORIGINS=True`, console email backend
  - `settings/production.py` — hardened (see Section 6)
- All secrets loaded from env: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `PAYSTACK_SECRET_KEY`, `FLUTTERWAVE_SECRET_KEY`, `EMAIL_HOST_PASSWORD`, `SMS_API_KEY`

### 2.2 Dependencies
Generate `requirements.txt` and `requirements-dev.txt`:

**Production:**
```
Django>=4.2,<5.0
djangorestframework>=3.14
django-cors-headers
django-filter
PyJWT
psycopg2-binary
python-decouple
celery[redis]
redis
django-redis
requests
gunicorn
django-db-connection-pool
```

**Development (additional):**
```
pytest
pytest-django
pytest-cov
pytest-xdist
factory-boy
faker
responses
black
isort
flake8
pre-commit
```

### 2.3 Background Tasks — Celery + Redis
- `celery.py` in project root with autodiscover
- `tasks.py` in each app for async operations
- Redis as broker (db 2) and result backend (db 3)
- Celery Beat for scheduled tasks (see Section 6.7)

### 2.4 Project Structure Change
```
backend/
├── school/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── celery.py          (NEW)
│   ├── urls.py
│   └── wsgi.py
├── services/              (NEW — shared utilities)
│   ├── __init__.py
│   ├── email.py           (SMTP/SendGrid sending)
│   ├── sms.py             (Termii/Africa's Talking)
│   └── cache.py           (cache helpers)
├── <each app>/
│   ├── services.py        (NEW — business logic)
│   ├── signals.py         (NEW — automation)
│   ├── tasks.py           (NEW — Celery tasks)
│   ├── admin.py           (POPULATED)
│   ├── tests/             (NEW — test directory)
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   ├── test_views.py
│   │   ├── test_signals.py
│   │   ├── test_tasks.py
│   │   └── factories.py
│   └── ... (existing files)
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── gunicorn.conf.py
├── pytest.ini
└── setup.cfg              (black, isort, flake8 config)
```

---

## 3. Service Layer & Business Logic

### 3.1 Pattern
Views become thin HTTP handlers. All business logic moves to `services.py`:

```python
# views.py — THIN
class StudentViewSet(viewsets.ModelViewSet):
    def create(self, request):
        data = StudentCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        student = StudentService.create_student(data.validated_data, request.user)
        return Response(StudentSerializer(student).data, status=201)

# services.py — THICK
class StudentService:
    @staticmethod
    def create_student(data, created_by):
        # matric number generation, validation, status checks, notifications
        ...
```

### 3.2 Service Classes Per App

**accounts/services.py:**
- `AuthService` — login with audit logging, token generation, password reset flow, account lockout after 5 failed attempts
- `UserService` — user CRUD with role validation, profile photo handling (size/type validation, UUID rename)

**students/services.py:**
- `StudentService` — create with auto matric number, status transitions (active/suspended/graduated/withdrawn), bulk CSV import
- `FacultyService` — CRUD with cascade protection (can't delete faculty with active students)
- `DepartmentService` — CRUD with HOD assignment validation
- `ProgrammeService` — CRUD with accreditation status check

**academic/services.py:**
- `SessionService` — create/activate (only one active at a time, auto-deactivate previous)
- `CourseService` — prerequisite checking, credit load validation (min/max per semester)
- `RegistrationService` — course registration with fee clearance check, deadline enforcement
- `ResultService` — grade entry validation (CA + Exam = 100), GPA/CGPA calculation, transcript generation, result publishing with notification trigger
- `AttendanceService` — mark attendance, generate reports, flag students below threshold

**finance/services.py:**
- `InvoiceService` — bulk generation per session/level, individual generation, overdue detection
- `PaymentService` — payment initiation with gateway abstraction, verification, receipt generation, installment tracking
- `ScholarshipService` — apply discounts to invoices, eligibility checking
- `FeeWaiverService` — approval workflow (request/review/approve/reject), partial waiver calculation
- `ReportService` — revenue summaries, payment trends, outstanding balances, programme-level breakdown

**library/services.py:**
- `BookService` — inventory management, copy tracking (available/borrowed/damaged/lost)
- `LoanService` — borrow with availability check, return with fine calculation (per-day overdue), auto-remind via Celery
- `ReservationService` — reserve with queue position, auto-expire after 48 hours

**hostel/services.py:**
- `AllocationService` — room assignment with capacity check, gender matching, session-based
- `RoomChangeService` — request/approval workflow, swap logic
- `FeeService` — hostel fee generation linked to room type

**hr/services.py:**
- `EmployeeService` — onboarding, department assignment, designation tracking
- `LeaveService` — request/HOD approval/HR approval chain, leave balance tracking, auto-deduct
- `PayrollService` — monthly salary calculation, deductions (tax, pension, loan), bulk generation
- `AttendanceService` — check-in/out, late tracking, monthly summary

**nuc/services.py:**
- `AccreditationService` — track status, expiry alerts
- `ComplianceService` — checklist management, completion percentage, gap analysis
- `ReportService` — generate NUC-format reports, graduation list export

**notifications/services.py:**
- `NotificationService` — create in-app notifications, mark read, bulk by audience
- `EmailService` — template rendering + SMTP sending via Celery
- `SMSService` — template rendering + SMS gateway via Celery
- `AnnouncementService` — targeted announcements (all/students/staff/department)

### 3.3 Django Signals (post_save)

| Signal | Trigger | Action |
|--------|---------|--------|
| `student_created` | Student.post_save (created=True) | Generate welcome notification + email |
| `course_registered` | CourseRegistration.post_save | Check fee clearance, update credit load |
| `result_published` | Result.post_save (status=published) | Notify student + parent, update GPA |
| `payment_confirmed` | Payment.post_save (status=confirmed) | Update invoice status, check full clearance |
| `leave_approved` | LeaveRequest.post_save (status=approved) | Update leave balance |
| `session_activated` | AcademicSession.post_save (is_active=True) | Deactivate previous session |

### 3.4 Celery Beat Triggers (not Django signals — periodic tasks)

| Task | Schedule | Action |
|------|----------|--------|
| `check_overdue_invoices` | Daily 8 AM | Flag overdue invoices, trigger payment reminder notifications |
| `check_overdue_books` | Daily 7 AM | Flag overdue loans, calculate fines, trigger reminder notifications |
| `expire_reservations` | Every 6 hours | Auto-cancel reservations older than 48 hours |

### 3.5 Strict Serializer Validation
Every serializer enforced:
- Field-level: email format, phone format (`+234` prefix), date ranges, matric number pattern
- Cross-field: `exam_score + ca_score = 100`, `end_date > start_date`, `capacity >= current_occupants`
- Read vs. Write serializer separation (list serializers lightweight, detail serializers full)
- Nested create/update support where needed

### 3.6 Bug Fixes
- `finance/views.py` line ~571: rename `total_waivered` to `total_waived`
- `Library.jsx` line 24: change `studentService.getFaculties` to `libraryService.getBooks`
- All admin.py files: register all models with proper list_display, list_filter, search_fields
- Fix silent `.catch(() => ({}))` in finance dashboard — surface errors properly

---

## 4. Frontend Modernization

### 4.1 TypeScript Migration
- Convert all `.jsx`/`.js` to `.tsx`/`.ts` with `strict: true`
- All API responses typed with interfaces matching backend serializers
- Component props, form data, auth context typed
- `tsconfig.json` added with strict configuration

### 4.2 State Management — Zustand Stores
```
stores/
├── authStore.ts         (replaces AuthContext)
├── studentStore.ts
├── academicStore.ts
├── financeStore.ts
├── libraryStore.ts
├── hostelStore.ts
├── hrStore.ts
├── nucStore.ts
├── notificationStore.ts
├── uiStore.ts           (sidebar, modals, active tab, loading)
```
Each store handles its own API calls, loading states, error states. Components become pure renderers.

### 4.3 Form Handling — react-hook-form + zod
Every form gets:
- Zod schema for validation rules
- react-hook-form for state management, dirty tracking
- Inline error messages with field highlighting
- Disabled submit until valid
- Loading spinner during submission

### 4.4 API Layer Rewrite
```
services/
├── api.ts               (typed axios instance + interceptors)
├── auth.api.ts
├── students.api.ts
├── academic.api.ts
├── finance.api.ts
├── library.api.ts
├── hostel.api.ts
├── hr.api.ts
├── nuc.api.ts
├── notifications.api.ts
```
Standardized error handling — API errors auto-mapped to toast notifications via interceptor.

### 4.5 Component Architecture
```
components/
├── ui/
│   ├── DataTable.tsx    (enhanced — sorting, column resize, export)
│   ├── Pagination.tsx
│   ├── ConfirmModal.tsx
│   ├── Skeleton.tsx
│   ├── Toast/
│   ├── FormField.tsx    (NEW — label + input + error wrapper)
│   ├── Select.tsx       (NEW — searchable, async options)
│   ├── DatePicker.tsx   (NEW — date/range picker)
│   ├── FileUpload.tsx   (NEW — drag-drop, preview, size validation)
│   ├── StatusBadge.tsx  (NEW)
│   ├── StatCard.tsx     (NEW — extracted from Dashboard)
│   ├── EmptyState.tsx   (NEW)
│   └── LoadingOverlay.tsx (NEW)
├── layout/
│   ├── Layout.tsx
│   ├── Sidebar.tsx      (extracted, collapsible)
│   ├── Header.tsx       (extracted, functional search + notifications)
│   └── Breadcrumb.tsx   (NEW)
├── shared/
│   ├── RoleGuard.tsx    (NEW — show/hide by user_type)
│   ├── ProtectedRoute.tsx (enhanced with role check)
│   └── ErrorBoundary.tsx (NEW)
```

### 4.6 Page Fixes — Currently Working (12 Pages)

| Page | Changes |
|------|---------|
| Login | Form validation, remember me, forgot password link |
| Dashboard | Replace all hardcoded data with real API calls, role-based widgets |
| Students | Add edit modal, bulk CSV import, export CSV/PDF, photo upload |
| Courses | Add edit capability, prerequisite display, allocation view |
| Results | Add edit/delete, bulk entry, GPA display per student, transcript view |
| Academic | Add semester create/edit, session activation toggle |
| Finance | Wire up Invoices + Payments tabs, add reports tab with charts |
| Faculties | Wire up actual API calls |
| Departments | Wire up actual API calls |
| Programmes | Wire up actual API calls |
| Users | Make edit/delete functional, add role-based filtering |
| Settings | Wire up to backend settings endpoint, persist changes |

### 4.7 Page Fixes — Currently Stub (4 Pages, Full Build)

| Page | Implementation |
|------|---------------|
| Library | Books CRUD with search, loan management (borrow/return/renew), reservation system, member management, overdue tracking with fine display |
| Hostel | Hostel/room CRUD, assignment workflow, room change request form + approval, fee management, occupancy dashboard with capacity bars |
| HR | Employee CRUD with department filter, leave request/approval workflow with calendar view, attendance check-in/out, payroll generation + history table |
| NUC | Accreditation status board with color-coded badges, compliance checklists with progress bars, report generation form, graduation list management |

### 4.8 Global Search (Header)
- Debounced input (300ms)
- Backend endpoint: `GET /api/search/?q=<term>` queries across Student, Course, Employee models
- Results grouped by category with click-to-navigate
- Keyboard shortcut: `Ctrl+K` to focus

### 4.9 Notification System (Bell Icon)
- Poll unread count every 30 seconds
- Dropdown panel with recent notifications
- Click to mark read + navigate to source
- "Mark all read" action
- Notification preferences in Settings page

### 4.10 Role-Based UI

| Role | Visible modules |
|------|----------------|
| admin | All modules, all CRUD operations |
| staff | Department-relevant modules, read-heavy |
| lecturer | Courses (allocated), Results (entry), Attendance (marking), Students (view) |
| student | Dashboard (personal), Course registration, Results (view), Finance (invoices/payments), Library (loans), Hostel (assignment) |
| parent | Dashboard (child's info), Results (view), Finance (view) |

### 4.11 Charts — Recharts
- Dashboard: enrollment trends (line), revenue overview (bar), attendance rates (area)
- Finance: collection vs. outstanding (pie), monthly trends (bar), programme breakdown (stacked bar)
- Academic: grade distribution per course (bar), GPA histogram (histogram)
- HR: attendance heatmap, leave utilization (donut)

---

## 5. Testing & CI/CD

### 5.1 Backend — pytest + pytest-django

**Libraries:** pytest, pytest-django, pytest-cov, pytest-xdist, factory_boy, faker, responses

**Coverage targets:** 80%+ on services, 70%+ overall

**Critical test areas:**

| Module | Tests |
|--------|-------|
| accounts | Login, token refresh, password reset, lockout, permissions |
| finance | Invoice generation, payment verification, installments, waivers |
| academic | Course registration + prerequisites, credit load, GPA/CGPA calc |
| students | Matric number generation, status transitions, cascade protection |
| library | Loan/return + fines, reservation queue, overdue detection |
| hostel | Capacity enforcement, gender matching, change request workflow |
| hr | Leave balance, payroll calculation, approval chain |
| nuc | Accreditation expiry, compliance percentage |

**Shared fixtures in `conftest.py`:** authenticated client, admin/student/lecturer users, active session/semester

### 5.2 Frontend — Vitest + React Testing Library

**Libraries:** vitest, @testing-library/react, @testing-library/user-event, msw, @testing-library/jest-dom

**Critical test areas:**

| Area | Tests |
|------|-------|
| Auth | Login, logout, token refresh, 401 redirect, role guard |
| Stores | State transitions, API integration, error handling |
| DataTable | Sort, filter, paginate, select, export |
| Forms | Validation, error display, submission, loading |
| Role UI | Admin vs. student vs. lecturer visibility |
| Each page | Renders, loads data, CRUD, error/empty states |

### 5.3 CI — GitHub Actions

```
Jobs:
  backend-lint:    flake8 + black + isort check
  backend-test:    PostgreSQL + Redis service containers, pytest --cov, fail < 70%
  frontend-lint:   ESLint + tsc --noEmit
  frontend-test:   vitest --coverage, fail < 70%
  frontend-build:  npm run build
  security-scan:   pip-audit + npm audit
```

### 5.4 Code Quality
- **Backend:** black (format), isort (imports), flake8 (lint), mypy (gradual types)
- **Frontend:** ESLint (strict TS rules), Prettier (format)
- **Pre-commit hooks:** all of the above run before commit

### 5.5 Deployment Pipeline
```
main push → CI green → build frontend → collectstatic → SSH to VPS →
  pull code → pip install → migrate → collectstatic → restart gunicorn →
  restart celery worker + beat → health check → notify
```

---

## 6. Production Readiness & Performance

### 6.1 Security Settings (production.py)
- `SECURE_SSL_REDIRECT = True`
- `SECURE_HSTS_SECONDS = 31536000`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = 'DENY'`
- `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`

### 6.2 Caching — Redis
| Cache | DB | TTL |
|-------|-----|-----|
| Sessions | 0 | session length |
| Dashboard stats | 1 | 5 min |
| Faculty/Dept/Prog lists | 1 | 1 hour |
| Current session | 1 | 30 min |
| Unread notification count | 1 | 30 sec |
| Celery broker | 2 | — |
| Celery results | 3 | — |

Cache invalidation via Django signals — model save invalidates related keys.

### 6.3 Database Optimization
- Connection pooling: `django-db-connection-pool` (POOL_SIZE=10, MAX_OVERFLOW=20)
- `select_related` / `prefetch_related` on all list views to eliminate N+1
- Dashboard: single aggregation query per stat (not Python loops)
- Finance reports: `.annotate()` aggregations

**New composite indexes:**
- Student: `(programme, level, status)`
- Invoice: `(student, session, status)`
- Payment: `(invoice, status, created_at)`
- Result: `(student, course, semester)`
- BookLoan: `(member, status)`
- Attendance: `(student, course, date)`
- Employee: `(department, status)`

### 6.4 Logging
- Rotating file handler: `/var/log/tims/app.log` (10MB, 5 backups)
- Separate error log: `/var/log/tims/error.log`
- Per-app log levels: accounts + finance at INFO, others at WARNING
- Celery task logging at INFO

### 6.5 Health Check Endpoint
`GET /api/health/` returns:
- Database connectivity
- Redis connectivity
- Celery worker alive
- Disk space
- 200 + JSON on success, 503 on failure

### 6.6 Audit Trail
- `AuditLog` model in accounts app
- Fields: user, action, model, object_id, old_values, new_values, ip_address, timestamp
- Auto-logged via middleware for all POST/PUT/PATCH/DELETE
- Admin-only API endpoint for querying

### 6.7 Celery Beat Schedule

| Task | Schedule |
|------|----------|
| Check overdue invoices | Daily 8 AM |
| Send payment reminders | Monday 9 AM |
| Check overdue books | Daily 7 AM |
| Expire reservations | Every 6 hours |
| Accreditation expiry alerts | Monday 8 AM |
| Cleanup orphan files | Sunday 2 AM |
| Daily attendance summary | Weekdays 6 PM |

### 6.8 File Handling
- Max size: 5MB photos, 10MB documents
- Allowed types: JPEG/PNG (photos), PDF/DOCX (documents)
- UUID-based filenames, sanitized
- Organized storage: `media/photos/`, `media/documents/`, `media/reports/`
- Periodic cleanup for orphaned files

### 6.9 Nginx Config
- SSL via Let's Encrypt, HTTP/2
- Frontend: serve `/dist` with `try_files` + 1-year cache for assets
- API + Admin: reverse proxy to Gunicorn on 127.0.0.1:8000
- Static/Media: direct serve with caching headers
- Security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- Gzip compression for text/CSS/JS/JSON/SVG

### 6.10 Gunicorn Config
- Bind: `127.0.0.1:8000`
- Workers: `2 * CPU + 1` (5 for 2-core VPS)
- Worker class: `gthread` with 2 threads
- Max requests: 1000 + jitter 50 (prevent memory leaks)
- Access + error logs to `/var/log/tims/`

### 6.11 Frontend Performance
- Vite code splitting: `React.lazy` + `Suspense` per route
- Vendor chunk separation (react, axios, zustand, recharts)
- Target: <200KB initial bundle, <50KB per lazy page
- `React.memo` on DataTable rows, stat cards
- Debounced search (300ms)
- `react-virtuoso` for lists with 1000+ rows
- Image lazy loading for profile photos
- Stale-while-revalidate in Zustand stores

### 6.12 Error Handling
**Backend:** Custom DRF exception handler with standardized format:
```json
{"error": "validation_error", "message": "...", "details": {...}}
```

**Frontend:**
- ErrorBoundary at route level
- API errors → toast notifications (5s auto-dismiss)
- Network errors → "Connection lost" banner + retry
- Form errors → inline field-level messages

---

## 7. New Backend Endpoint

### Global Search
`GET /api/search/?q=<term>` — queries across Student (name, matric), Course (code, name), Employee (name, staff_id). Returns results grouped by category. Admin only for full results; role-filtered for other users.

### Settings Persistence
`GET/PUT /api/settings/` — system configuration (branding, academic defaults, notification preferences). Stored in a `SystemConfig` singleton model. Admin only.

---

## 8. Out of Scope (Deferred)

- JAMB CAPS API integration
- Remita payment gateway
- NUC external reporting API
- NYSC coordination
- Government agency reporting (FME, NBS, ICPC/EFCC, TSA)
- WebSocket real-time notifications (polling used instead)
- Mobile app
- Multi-tenancy (single institution deployment)

These are designed as integration points — the service layer has clear boundaries where external APIs plug in later.

---

## 9. Implementation Order

1. **Foundation** — env config, settings split, requirements, Celery setup
2. **Backend service layer** — services.py + signals.py + tasks.py for all 9 apps, fix all bugs, register all admin models
3. **Backend testing** — pytest setup, factories, critical path tests
4. **Frontend TypeScript migration** — convert all files, add types
5. **Frontend state + API rewrite** — Zustand stores, typed API layer
6. **Frontend page completion** — wire up all 17 pages, build 4 stub pages
7. **Frontend components** — new shared components, role-based UI, charts
8. **Integration testing** — end-to-end flows, Vitest + MSW
9. **Production config** — Nginx, Gunicorn, systemd, CI/CD
10. **Performance** — caching, query optimization, bundle optimization
