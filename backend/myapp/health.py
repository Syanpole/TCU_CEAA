from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Health check endpoint for Kubernetes liveness/readiness probes
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "cache": "unknown"
    }
    
    status_code = 200
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "error"
        health_status["status"] = "unhealthy"
        status_code = 503
    
    # Check Redis/cache (optional)
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status["cache"] = "connected"
    except Exception as e:
        health_status["cache"] = "error"
        # Don't fail health check if cache is down
    
    return JsonResponse(health_status, status=status_code)

@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check - returns 200 when app is ready to serve requests
    """
    return JsonResponse({"status": "ready"}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check - returns 200 if app is alive
    """
    return JsonResponse({"status": "alive"}, status=200)
