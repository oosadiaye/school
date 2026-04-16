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
