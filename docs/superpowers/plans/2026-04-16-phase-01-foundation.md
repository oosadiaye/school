# Phase 1: Foundation & Bug Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish production-ready foundation — environment config, settings split, Celery+Redis, pytest setup, git repository, and fix all Tier-1 runtime bugs — without breaking existing functionality.

**Architecture:** Split monolithic `settings.py` into `settings/base.py` + `settings/development.py` + `settings/production.py` with env vars via python-decouple. Add Celery app module with Redis broker. Initialize pytest-django with factory_boy for the test infrastructure all subsequent phases depend on.

**Tech Stack:** Django 4.x, python-decouple, Celery+Redis, pytest-django, factory_boy, Docker Compose (dev only)

**Spec Reference:** `docs/superpowers/specs/2026-04-02-tims-production-readiness-design.md` §2, §3.6

---

## File Map

**Create:**
- `backend/.env.example` — environment template (committed)
- `backend/.env` — local secrets (git-ignored)
- `backend/.gitignore` — Python/Django ignore rules
- `backend/requirements.txt` — production dependencies
- `backend/requirements-dev.txt` — dev dependencies
- `backend/school/settings/__init__.py` — package init
- `backend/school/settings/base.py` — shared settings
- `backend/school/settings/development.py` — dev settings
- `backend/school/settings/production.py` — prod settings
- `backend/school/celery.py` — Celery app
- `backend/pytest.ini` — pytest config
- `backend/setup.cfg` — black/isort/flake8 config
- `backend/conftest.py` — shared pytest fixtures
- `backend/accounts/tests/__init__.py` — enable test discovery
- `backend/accounts/tests/factories.py` — user factories
- `backend/accounts/tests/test_smoke.py` — sanity check tests
- `backend/core/__init__.py` — new shared app
- `backend/core/apps.py` — core app config
- `backend/core/views.py` — health check view
- `backend/core/urls.py` — core URL routes
- `backend/core/tests/__init__.py`
- `backend/core/tests/test_health.py` — health endpoint test
- `.gitignore` — repo root gitignore
- `docker-compose.dev.yml` — local PostgreSQL + Redis

**Modify:**
- `backend/school/settings.py` — DELETE (replaced by settings/ package)
- `backend/school/__init__.py` — import celery app
- `backend/school/urls.py` — add core.urls routing
- `backend/school/wsgi.py` — point to new settings module
- `backend/school/asgi.py` — point to new settings module
- `backend/manage.py` — point to new settings module
- `backend/finance/views.py:571` — fix `total_waivered` typo
- `backend/finance/views.py:555-573` — also fix logic to use computed variable
- `frontend/src/pages/Library.jsx:2,24` — fix wrong API import/call
- `frontend/src/pages/Finance.jsx` — remove silent `.catch(() => ({data:{}}))`

---

## Task 1: Initialize Git Repository at Project Root

**Files:**
- Create: `.gitignore` (project root)
- Create: `backend/.gitignore`

**Why:** Project is not a git repo yet. We need version control before any other change so we can commit atomically per task.

- [ ] **Step 1.1: Create project-root `.gitignore`**

Write to `C:/Users/USER/Documents/Antigravity/school/.gitignore`:
```gitignore
# OS
.DS_Store
Thumbs.db
desktop.ini
nul

# IDE
.idea/
.vscode/
*.iml

# Logs
admin_output.txt
admin_error.txt
*.log

# Environment
**/.env
**/.env.local
!**/.env.example

# Dependencies
**/node_modules/
**/venv/
**/__pycache__/

# Build outputs
**/dist/
**/build/
**/*.egg-info/

# Django
**/media/
**/staticfiles/
**/db.sqlite3

# Testing
**/.coverage
**/htmlcov/
**/.pytest_cache/

# Superpowers (brainstorm companion state)
.superpowers/
```

- [ ] **Step 1.2: Create backend-specific `.gitignore`**

Write to `backend/.gitignore`:
```gitignore
*.pyc
__pycache__/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
venv/
.venv/
env/
.env
media/uploads/
staticfiles/
celerybeat-schedule
*.log
```

- [ ] **Step 1.3: Initialize git and set up remote**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git init
git config user.name "TIMS Developer"
git config user.email "dev@tims.local"
git branch -M main
git remote add origin https://github.com/oosadiaye/school.git 2>/dev/null || git remote set-url origin https://github.com/oosadiaye/school.git
```

Expected: No errors. `git remote -v` should show origin twice (fetch + push).

- [ ] **Step 1.4: First commit — existing code baseline**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add .gitignore backend/.gitignore
git add NIGERIA_UNIVERSITY_MANAGEMENT_SYSTEM_PLAN.md start_server.bat
git add docs/
git add backend/ frontend/ -f
git status  # review
git commit -m "chore: initial baseline snapshot of TIMS codebase"
```

Expected: Commit created with all existing files under version control. `.env`, `venv/`, `node_modules/`, `__pycache__/` excluded automatically.

---

## Task 2: Create python-decouple Environment Config

**Files:**
- Create: `backend/.env.example`
- Create: `backend/.env`

**Why:** All secrets currently hardcoded in `settings.py`. Must load from env file via python-decouple before splitting settings.

- [ ] **Step 2.1: Install python-decouple in venv**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pip install python-decouple
```

Expected: Successfully installed python-decouple-3.x.

- [ ] **Step 2.2: Write `.env.example` (committed template)**

Write to `backend/.env.example`:
```dotenv
# Django
DJANGO_SETTINGS_MODULE=school.settings.development
SECRET_KEY=change-me-to-a-50-char-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=school
DB_USER=school
DB_PASSWORD=school
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# JWT
JWT_ACCESS_TOKEN_HOURS=2
JWT_REFRESH_TOKEN_DAYS=7

# Redis / Celery
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/3

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@tims.local

# Payment Gateways
PAYSTACK_PUBLIC_KEY=
PAYSTACK_SECRET_KEY=
FLUTTERWAVE_PUBLIC_KEY=
FLUTTERWAVE_SECRET_KEY=
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=

# SMS
SMS_PROVIDER=termii
SMS_API_KEY=
SMS_SENDER_ID=TIMS
```

- [ ] **Step 2.3: Create local `.env` by copying the example**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
cp .env.example .env
```

- [ ] **Step 2.4: Generate a real SECRET_KEY and put it in `.env`**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Expected: A 50-character random string. Copy it. Then edit `backend/.env` and replace the `SECRET_KEY=change-me-...` line with `SECRET_KEY=<the-generated-string>`.

- [ ] **Step 2.5: Commit**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add backend/.env.example
git status  # verify .env is NOT staged
git commit -m "feat(config): add .env.example template for environment variables"
```

Expected: Only `.env.example` committed. `.env` must be ignored.

---

## Task 3: Create Settings Package (Split base/dev/prod)

**Files:**
- Create: `backend/school/settings/__init__.py`
- Create: `backend/school/settings/base.py`
- Create: `backend/school/settings/development.py`
- Create: `backend/school/settings/production.py`
- Delete: `backend/school/settings.py`

**Why:** Monolithic `settings.py` has `DEBUG=True` and hardcoded credentials. Split lets us have safe dev defaults and hardened prod without code changes.

- [ ] **Step 3.1: Create settings package init**

Write to `backend/school/settings/__init__.py`:
```python
# Settings package — actual settings in base.py, development.py, production.py
# Set DJANGO_SETTINGS_MODULE to one of:
#   school.settings.development  (local dev)
#   school.settings.production   (deploy)
```

- [ ] **Step 3.2: Create `base.py` with shared settings**

Write to `backend/school/settings/base.py`:
```python
"""
Base Django settings for TIMS.
Shared across all environments. Inherit from here.
"""
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Loaded per-environment, default provided for safety
SECRET_KEY = config('SECRET_KEY', default='unsafe-default-override-in-env')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    # Project apps
    'core',
    'accounts',
    'students',
    'academic',
    'finance',
    'library',
    'hostel',
    'hr',
    'nuc',
    'notifications',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'school.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'school.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='school'),
        'USER': config('DB_USER', default='school'),
        'PASSWORD': config('DB_PASSWORD', default='school'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'login': '5/minute',
    },
}

# JWT
JWT_SECRET_KEY = SECRET_KEY
JWT_ACCESS_TOKEN_LIFETIME = timedelta(
    hours=config('JWT_ACCESS_TOKEN_HOURS', default=2, cast=int))
JWT_REFRESH_TOKEN_LIFETIME = timedelta(
    days=config('JWT_REFRESH_TOKEN_DAYS', default=7, cast=int))

# CORS — overridden per environment
CORS_ALLOW_CREDENTIALS = True

# Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/2')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email — defaults for dev, overridden in production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@tims.local')

# Payment gateway keys — loaded even if unused (services module reads them)
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='')
FLUTTERWAVE_PUBLIC_KEY = config('FLUTTERWAVE_PUBLIC_KEY', default='')
FLUTTERWAVE_SECRET_KEY = config('FLUTTERWAVE_SECRET_KEY', default='')
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')

# SMS
SMS_PROVIDER = config('SMS_PROVIDER', default='termii')
SMS_API_KEY = config('SMS_API_KEY', default='')
SMS_SENDER_ID = config('SMS_SENDER_ID', default='TIMS')
```

- [ ] **Step 3.3: Create `development.py`**

Write to `backend/school/settings/development.py`:
```python
"""Development settings — permissive, debug on, console email."""
from .base import *  # noqa: F401,F403
from decouple import config, Csv

DEBUG = True

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0',
    cast=Csv()
)

# Dev CORS — permissive for local Vite
CORS_ALLOW_ALL_ORIGINS = True
```

- [ ] **Step 3.4: Create `production.py`**

Write to `backend/school/settings/production.py`:
```python
"""Production settings — hardened, SSL enforced, tight CORS."""
from .base import *  # noqa: F401,F403
from decouple import config, Csv

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
if not ALLOWED_HOSTS:
    raise RuntimeError('ALLOWED_HOSTS must be set in production')

# Tight CORS — only whitelisted frontend origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

# SSL / HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Real SMTP email in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
```

- [ ] **Step 3.5: Point manage.py / wsgi.py / asgi.py to new settings**

Modify `backend/manage.py`:
Find: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')`
Replace with: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings.development')`

Modify `backend/school/wsgi.py`:
Find: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')`
Replace with: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings.production')`

Modify `backend/school/asgi.py` (if exists — similar change to wsgi.py).

- [ ] **Step 3.6: Delete old monolithic settings.py**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend/school"
rm settings.py
```

- [ ] **Step 3.7: Temporarily omit `core` from INSTALLED_APPS (re-added in Task 4)**

The `core` app doesn't exist yet. In `backend/school/settings/base.py` INSTALLED_APPS list, remove the `'core',` line for now. It will be re-added in Step 4.2a below, after the app directory exists.

- [ ] **Step 3.8: Run Django check**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3.9: Commit**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add backend/school/settings/ backend/school/__init__.py backend/school/wsgi.py backend/school/asgi.py backend/manage.py
git rm backend/school/settings.py
git commit -m "refactor(config): split settings into base/development/production modules"
```

---

## Task 4: Create `core` Shared App

**Files:**
- Create: `backend/core/__init__.py`
- Create: `backend/core/apps.py`
- Create: `backend/core/views.py`
- Create: `backend/core/urls.py`
- Create: `backend/core/tests/__init__.py`
- Create: `backend/core/tests/test_health.py`

**Why:** Need a shared app for cross-cutting utilities (health check, search endpoint, settings endpoint). Phase 1 only implements the health check; others come in later phases.

- [ ] **Step 4.1: Create `core/__init__.py`**

Write to `backend/core/__init__.py`:
```python
# Core app — shared utilities, health checks, cross-cutting endpoints
```

- [ ] **Step 4.2: Create `core/apps.py`**

Write to `backend/core/apps.py`:
```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
```

- [ ] **Step 4.2a: Re-add `core` to INSTALLED_APPS**

In `backend/school/settings/base.py`, find the INSTALLED_APPS list and add `'core',` as the first entry under "Project apps" (before `'accounts',`). The list should now include:
```python
    # Project apps
    'core',
    'accounts',
    'students',
    # ... rest unchanged
```

Verify no import errors:
```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 4.3: Write failing test first — `core/tests/test_health.py`**

Write to `backend/core/tests/__init__.py` (empty file).

Write to `backend/core/tests/test_health.py`:
```python
"""Tests for health check endpoint."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_endpoint_returns_200(client):
    """Health endpoint responds 200 OK with status JSON."""
    url = reverse('core:health')
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'checks' in data
    assert data['checks']['database'] is True


@pytest.mark.django_db
def test_health_endpoint_includes_redis_check(client):
    """Health endpoint reports redis connectivity status."""
    url = reverse('core:health')
    response = client.get(url)
    data = response.json()
    assert 'redis' in data['checks']
```

- [ ] **Step 4.4: Run test to verify it fails**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest core/tests/test_health.py -v
```

Expected: FAIL with `NoReverseMatch: 'core' is not a registered namespace` (tests can't find URL yet).

- [ ] **Step 4.5: Implement `core/views.py`**

Write to `backend/core/views.py`:
```python
"""Core views — health check, root utilities."""
from django.db import connection
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def _check_database() -> bool:
    """Verify database connectivity with a trivial query."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    """Verify Redis connectivity by pinging the Celery broker URL."""
    try:
        import redis
        client = redis.from_url(settings.CELERY_BROKER_URL)
        return bool(client.ping())
    except Exception:
        return False


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """System health endpoint — used by load balancer / monitoring."""
    checks = {
        'database': _check_database(),
        'redis': _check_redis(),
    }
    status = 'ok' if all(checks.values()) else 'degraded'
    http_status = 200 if status == 'ok' else 503
    return Response({'status': status, 'checks': checks}, status=http_status)
```

- [ ] **Step 4.6: Implement `core/urls.py`**

Write to `backend/core/urls.py`:
```python
"""URL routes for the core app."""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.health, name='health'),
]
```

- [ ] **Step 4.7: Wire core URLs into project `school/urls.py`**

Modify `backend/school/urls.py` — add `path('api/', include('core.urls'))` before the other `api/` includes. The final file should include `path('api/', include('core.urls')),` with the rest of the existing includes unchanged.

Edit `backend/school/urls.py` — find the `urlpatterns = [` block and add the line as the first `api/` entry:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/accounts/', include('accounts.urls')),
    # ... existing includes below unchanged
```

- [ ] **Step 4.8: Run tests to verify pass**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest core/tests/test_health.py -v
```

Expected: `test_health_endpoint_returns_200 PASSED`. Second test will fail if Redis isn't running locally — that's fine, we run Redis in Task 7.

- [ ] **Step 4.9: Commit**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add backend/core/ backend/school/urls.py backend/school/settings/base.py
git commit -m "feat(core): add core app with health check endpoint"
```

---

## Task 5: Generate `requirements.txt` and `requirements-dev.txt`

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`

**Why:** No dependency manifest currently exists. Without this, deployment is impossible.

- [ ] **Step 5.1: Install new dependencies in venv**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pip install celery[redis] redis django-redis django-filter gunicorn requests
pip install pytest pytest-django pytest-cov pytest-xdist factory-boy faker responses black isort flake8
```

- [ ] **Step 5.2: Write `requirements.txt` explicitly (no pip freeze to avoid dev deps)**

Write to `backend/requirements.txt`:
```
Django>=4.2,<5.0
djangorestframework>=3.14
django-cors-headers>=4.3
django-filter>=23.0
PyJWT>=2.8
psycopg2-binary>=2.9
python-decouple>=3.8
celery[redis]>=5.3
redis>=5.0
django-redis>=5.4
requests>=2.31
gunicorn>=21.2
```

- [ ] **Step 5.3: Write `requirements-dev.txt`**

Write to `backend/requirements-dev.txt`:
```
-r requirements.txt

# Testing
pytest>=7.4
pytest-django>=4.7
pytest-cov>=4.1
pytest-xdist>=3.5
factory-boy>=3.3
faker>=22.0
responses>=0.24

# Linting / formatting
black>=23.12
isort>=5.13
flake8>=7.0
pre-commit>=3.6
```

- [ ] **Step 5.4: Verify install from requirements files works**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pip install -r requirements-dev.txt
```

Expected: `Requirement already satisfied` for all (we just installed them). No errors.

- [ ] **Step 5.5: Commit**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add backend/requirements.txt backend/requirements-dev.txt
git commit -m "build(deps): add requirements.txt and requirements-dev.txt"
```

---

## Task 6: Set Up pytest-django Configuration

**Files:**
- Create: `backend/pytest.ini`
- Create: `backend/setup.cfg`
- Create: `backend/conftest.py`

**Why:** pytest is installed but not configured. Need `DJANGO_SETTINGS_MODULE` pointed correctly and shared fixtures available for all subsequent test tasks.

- [ ] **Step 6.1: Create `pytest.ini`**

Write to `backend/pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = school.settings.development
python_files = tests.py test_*.py *_tests.py
addopts = --strict-markers --reuse-db -ra
testpaths = .
markers =
    slow: marks tests as slow (deselect with -m "not slow")
    integration: marks integration tests (requires DB + Redis)
```

- [ ] **Step 6.2: Create `setup.cfg` for black/isort/flake8 config**

Write to `backend/setup.cfg`:
```ini
[flake8]
max-line-length = 100
exclude = venv,migrations,__pycache__,.git
ignore = E203,W503

[isort]
profile = black
line_length = 100
skip = venv,migrations

[tool:black]
line-length = 100
exclude = venv|migrations
```

- [ ] **Step 6.3: Create `conftest.py` with shared fixtures**

Write to `backend/conftest.py`:
```python
"""Shared pytest fixtures for all tests."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    """Unauthenticated DRF APIClient."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Create an admin user for tests."""
    return User.objects.create_superuser(
        username='admin_test',
        email='admin@test.local',
        password='TestPass12345!',
        first_name='Admin',
        last_name='User',
        user_type='admin',
    )


@pytest.fixture
def student_user(db):
    """Create a regular student user for tests."""
    return User.objects.create_user(
        username='student_test',
        email='student@test.local',
        password='TestPass12345!',
        first_name='Student',
        last_name='User',
        user_type='student',
    )


@pytest.fixture
def authed_admin_client(api_client, admin_user):
    """APIClient authenticated as admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def authed_student_client(api_client, student_user):
    """APIClient authenticated as student user."""
    api_client.force_authenticate(user=student_user)
    return api_client
```

- [ ] **Step 6.4: Run a sanity check test**

Create `backend/accounts/tests/__init__.py` (empty file).

Create `backend/accounts/tests/test_smoke.py`:
```python
"""Smoke tests confirming pytest + Django wiring works."""
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_can_create_user(admin_user):
    """Admin fixture creates a valid user."""
    User = get_user_model()
    assert User.objects.filter(username='admin_test').exists()
    assert admin_user.user_type == 'admin'


@pytest.mark.django_db
def test_authed_client_works(authed_admin_client):
    """Admin client can hit a protected endpoint."""
    response = authed_admin_client.get('/api/accounts/users/me/')
    assert response.status_code == 200
```

- [ ] **Step 6.5: Delete boilerplate `accounts/tests.py`**

The existing `backend/accounts/tests.py` is a Django boilerplate stub. Remove it now that we have `accounts/tests/` package.

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
rm accounts/tests.py
```

- [ ] **Step 6.6: Run smoke tests**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest accounts/tests/test_smoke.py -v
```

Expected: Both tests PASS.

- [ ] **Step 6.7: Commit**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add backend/pytest.ini backend/setup.cfg backend/conftest.py backend/accounts/tests/
git rm backend/accounts/tests.py
git commit -m "test(infra): configure pytest-django with shared fixtures and smoke tests"
```

---

## Task 7: Add Docker Compose for Local Services

**Files:**
- Create: `docker-compose.dev.yml` (project root)

**Why:** Local dev needs PostgreSQL and Redis running. Rather than require devs to install them, use Docker Compose for reproducibility. Task 4's Redis health check test will actually pass once this is running.

- [ ] **Step 7.1: Write `docker-compose.dev.yml`**

Write to `C:/Users/USER/Documents/Antigravity/school/docker-compose.dev.yml`:
```yaml
# Local development services — PostgreSQL + Redis
# Start: docker compose -f docker-compose.dev.yml up -d
# Stop:  docker compose -f docker-compose.dev.yml down

version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    container_name: tims_postgres_dev
    environment:
      POSTGRES_DB: school
      POSTGRES_USER: school
      POSTGRES_PASSWORD: school
    ports:
      - "5432:5432"
    volumes:
      - tims_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U school -d school"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: tims_redis_dev
    ports:
      - "6379:6379"
    volumes:
      - tims_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  tims_postgres_data:
  tims_redis_data:
```

- [ ] **Step 7.2: Start services**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps
```

Expected: Two containers `Up (healthy)`. **If Docker is not available**, document that the developer must install PostgreSQL + Redis natively or use existing instances (they already have PostgreSQL running based on the existing settings).

- [ ] **Step 7.3: Verify health endpoint now reports Redis OK**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
python manage.py runserver 8000 &
# In another terminal:
curl http://localhost:8000/api/health/
```

Expected: `{"status":"ok","checks":{"database":true,"redis":true}}`

- [ ] **Step 7.4: Re-run health tests**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest core/tests/test_health.py -v
```

Expected: Both health tests PASS.

- [ ] **Step 7.5: Commit**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add docker-compose.dev.yml
git commit -m "build(dev): add docker-compose for local postgres and redis"
```

---

## Task 8: Set Up Celery App Module

**Files:**
- Create: `backend/school/celery.py`
- Modify: `backend/school/__init__.py`
- Create: `backend/core/tasks.py`
- Create: `backend/core/tests/test_tasks.py`

**Why:** No async task runner exists. All long-running operations (bulk invoices, emails, reminders) currently block request threads. Celery+Redis fixes this; Phase 2 will start adding real tasks.

- [ ] **Step 8.1: Write failing test first — `core/tests/test_tasks.py`**

Write to `backend/core/tests/test_tasks.py`:
```python
"""Tests for Celery infrastructure via a simple ping task."""
import pytest
from core.tasks import ping


def test_ping_task_runs_synchronously_via_apply():
    """Confirm Celery task can be invoked (sync mode for tests)."""
    result = ping.apply(args=['hello']).get()
    assert result == 'pong: hello'


def test_ping_task_is_registered():
    """Confirm Celery app sees the task."""
    from school.celery import app
    assert 'core.tasks.ping' in app.tasks
```

- [ ] **Step 8.2: Run test to verify it fails**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest core/tests/test_tasks.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'core.tasks'` or `No module named 'school.celery'`.

- [ ] **Step 8.3: Create Celery app in `school/celery.py`**

Write to `backend/school/celery.py`:
```python
"""Celery app configuration for TIMS."""
import os
from celery import Celery

# Default settings module for 'celery' CLI command
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings.development')

app = Celery('school')

# Load settings from Django with CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in each installed app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Print task request — useful for debugging worker setup."""
    print(f'Request: {self.request!r}')
```

- [ ] **Step 8.4: Register Celery app in `school/__init__.py`**

Modify `backend/school/__init__.py`:
```python
"""School project package — exposes celery app for auto-discovery."""
from .celery import app as celery_app

__all__ = ('celery_app',)
```

- [ ] **Step 8.5: Create `core/tasks.py` with ping task**

Write to `backend/core/tasks.py`:
```python
"""Shared Celery tasks for the core app."""
from celery import shared_task


@shared_task
def ping(payload: str = 'hello') -> str:
    """Sanity check task — returns the input with a pong prefix."""
    return f'pong: {payload}'
```

- [ ] **Step 8.6: Run test to verify it passes**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest core/tests/test_tasks.py -v
```

Expected: Both tests PASS.

- [ ] **Step 8.7: Smoke test the Celery worker end-to-end**

In one terminal:
```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
celery -A school worker --loglevel=info --pool=solo
```

Expected: Worker starts, prints `celery@<hostname> ready.` and lists `[tasks]` including `core.tasks.ping`.

In another terminal:
```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
python manage.py shell -c "from core.tasks import ping; print(ping.delay('world').get(timeout=10))"
```

Expected: `pong: world` printed. Stop the worker with Ctrl+C.

- [ ] **Step 8.8: Commit**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add backend/school/celery.py backend/school/__init__.py backend/core/tasks.py backend/core/tests/test_tasks.py
git commit -m "feat(async): integrate celery with redis broker and ping task"
```

---

## Task 9: Fix Critical Runtime Bugs

**Files:**
- Modify: `backend/finance/views.py:562-573`
- Modify: `frontend/src/pages/Library.jsx:2,24`
- Modify: `frontend/src/pages/Finance.jsx` (locate silent catch)

**Why:** Tier-1 bugs from the audit. These are blocking production. Separate commits per bug so rollback is surgical.

- [ ] **Step 9.1: Write failing test for waivers_report endpoint**

Write to `backend/finance/tests/__init__.py` (empty file, if not exists).

Write to `backend/finance/tests/test_views_report.py`:
```python
"""Tests for finance reports endpoints."""
import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_waivers_report_does_not_crash(authed_admin_client):
    """waivers_report must not raise NameError for undefined `total_waivered`."""
    response = authed_admin_client.get('/api/finance/reports/waivers_report/')
    assert response.status_code == 200
    data = response.json()
    assert 'total_waivers' in data
    assert 'total_amount_waived' in data
    assert 'pending_waivers' in data
    assert data['total_amount_waived'] == 0  # no waivers in test DB
```

(Also delete `backend/finance/tests.py` if it's a boilerplate stub. Keep the package style.)

- [ ] **Step 9.2: Run test to confirm the crash**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest finance/tests/test_views_report.py -v
```

Expected: FAIL with `NameError: name 'total_waivered' is not defined`.

- [ ] **Step 9.3: Fix the typo in `finance/views.py`**

Modify `backend/finance/views.py` around line 571.

Find:
```python
        return Response({
            'total_waivers': FeeWaiver.objects.filter(is_approved=True).count(),
            'total_amount_waived': float(total_waivered),
            'pending_waivers': FeeWaiver.objects.filter(is_approved=False).count()
        })
```

Replace with:
```python
        return Response({
            'total_waivers': FeeWaiver.objects.filter(is_approved=True).count(),
            'total_amount_waived': float(total_waived),
            'pending_waivers': FeeWaiver.objects.filter(is_approved=False).count()
        })
```

- [ ] **Step 9.4: Run test to verify fix**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest finance/tests/test_views_report.py -v
```

Expected: PASS.

- [ ] **Step 9.5: Commit the finance fix**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add backend/finance/views.py backend/finance/tests/
git rm -f backend/finance/tests.py 2>/dev/null || true
git commit -m "fix(finance): correct undefined variable in waivers_report (total_waivered -> total_waived)"
```

- [ ] **Step 9.6: Fix `Library.jsx` wrong API call**

Modify `frontend/src/pages/Library.jsx`:

Find line 2:
```javascript
import { studentService } from '../services/api';
```

Replace with:
```javascript
import { libraryService } from '../services/api';
```

Find line 24 (`await studentService.getFaculties()`):
```javascript
      const response = await studentService.getFaculties();
```

Replace with:
```javascript
      const response = await libraryService.getBooks();
```

Also replace the alert-based handleSubmit so it doesn't fake success. Find:
```javascript
  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Book added successfully!');
    setShowForm(false);
    setFormData({ title: '', author: '', isbn: '', category: '', quantity: 1, available: 1, shelf_location: '' });
    fetchBooks();
  };
```

Replace with:
```javascript
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await libraryService.createBook(formData);
      setShowForm(false);
      setFormData({ title: '', author: '', isbn: '', category: '', quantity: 1, available: 1, shelf_location: '' });
      await fetchBooks();
    } catch (error) {
      console.error('Error creating book:', error);
    }
  };
```

- [ ] **Step 9.7: Smoke test the frontend build**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/frontend"
npm run build
```

Expected: Build succeeds with no errors. (Deeper Library refactor happens in Phase 7; here we just stop the broken API call.)

- [ ] **Step 9.8: Commit Library fix**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add frontend/src/pages/Library.jsx
git commit -m "fix(frontend): Library page calls libraryService.getBooks instead of studentService.getFaculties"
```

- [ ] **Step 9.9: Remove silent error catching in Finance.jsx**

Open `frontend/src/pages/Finance.jsx` and search for the string `.catch(() => ({ data: {} }))` or `.catch(() => ({data:{}}))`.

Replace each occurrence like:
```javascript
const dashboardRes = await financeService.getFinanceDashboard().catch(() => ({ data: {} }));
```

with:
```javascript
let dashboardRes;
try {
  dashboardRes = await financeService.getFinanceDashboard();
} catch (error) {
  console.error('Failed to load finance dashboard:', error);
  dashboardRes = { data: {} };
}
```

This preserves behavior but surfaces the error to the console (and later, to a toast in Phase 7).

- [ ] **Step 9.10: Commit Finance fix**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git add frontend/src/pages/Finance.jsx
git commit -m "fix(frontend): surface finance dashboard errors instead of silently swallowing"
```

---

## Task 10: Phase 1 Verification & Push

**Files:** None — verification only.

**Why:** Confirm Phase 1 produces working software before moving to Phase 2.

- [ ] **Step 10.1: Full backend test suite**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
pytest -v
```

Expected: All tests PASS. Count should match Phase 1 tests added (~5 tests across core + accounts + finance).

- [ ] **Step 10.2: Django deploy check against production settings**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
DJANGO_SETTINGS_MODULE=school.settings.production ALLOWED_HOSTS=example.com CORS_ALLOWED_ORIGINS=https://example.com EMAIL_HOST=smtp.example.com EMAIL_HOST_USER=x EMAIL_HOST_PASSWORD=x python manage.py check --deploy
```

**On Windows PowerShell** — use `$env:DJANGO_SETTINGS_MODULE="school.settings.production"` etc., or run from the `.env` file with appropriate values.

Expected: No critical warnings (some warnings are OK — we add more hardening in Phase 10).

- [ ] **Step 10.3: Frontend build**

```bash
cd "C:/Users/USER/Documents/Antigravity/school/frontend"
npm run build
```

Expected: Build completes; `dist/` directory populated; bundle size reported.

- [ ] **Step 10.4: Manual smoke test**

Start the backend dev server:
```bash
cd "C:/Users/USER/Documents/Antigravity/school/backend"
venv\Scripts\activate
python manage.py runserver 8000
```

In another terminal, start the frontend:
```bash
cd "C:/Users/USER/Documents/Antigravity/school/frontend"
npm run dev
```

Open `http://localhost:5173` in a browser:
- [ ] Login page renders
- [ ] Login with an existing account works (reset via `python manage.py shell` if needed)
- [ ] Dashboard loads without crashing
- [ ] Hit `http://localhost:8000/api/health/` in a new tab → `{"status":"ok",...}`
- [ ] Hit `http://localhost:8000/api/finance/reports/waivers_report/` (admin logged in) → returns JSON, no 500

Stop servers.

- [ ] **Step 10.5: Push Phase 1 to GitHub**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git log --oneline
git push -u origin main
```

Expected: All Phase 1 commits pushed. Confirm at `https://github.com/oosadiaye/school`.

- [ ] **Step 10.6: Tag Phase 1 completion**

```bash
cd "C:/Users/USER/Documents/Antigravity/school"
git tag -a phase-1-foundation -m "Phase 1: Foundation and bug fixes complete"
git push origin phase-1-foundation
```

---

## Phase 1 Completion Checklist

Before declaring Phase 1 done and starting Phase 2:

- [ ] `git status` shows clean working tree
- [ ] `pytest` passes all tests in `backend/`
- [ ] `python manage.py check` passes (dev settings)
- [ ] `python manage.py check --deploy` passes (production settings, with env vars set)
- [ ] `npm run build` succeeds in `frontend/`
- [ ] Manual smoke test completed (login + dashboard + health check + waivers_report)
- [ ] All commits pushed to `origin/main`
- [ ] `phase-1-foundation` tag exists on GitHub
- [ ] Master plan (`2026-04-16-master-plan.md`) updated: mark Phase 1 as `✅ Complete`

---

## What's Still Broken After Phase 1 (Intentional)

Phase 1 is a foundation, not a feature complete pass. These remain broken and will be fixed in later phases:
- Library, Hostel, HR, NUC pages still show stub data (Phase 7)
- Dashboard hardcoded data (Phase 7)
- Finance invoices/payments tabs still empty (Phase 7)
- Business logic still in views (Phase 2)
- No email/SMS actually sends (Phase 3)
- No admin UI registrations (Phase 4)
- No TypeScript (Phase 5)
- No role-based UI (Phase 8)
- No CI/CD (Phase 10)

These are documented in the master plan and their respective phase plans.
