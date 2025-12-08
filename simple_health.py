"""
Ultra-simple health check that ALWAYS returns 200 OK
No database, no dependencies, just a simple HTTP response
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    """Minimal health check - always returns OK"""
    return JsonResponse({"status": "ok"}, status=200)

@csrf_exempt  
def ready_check(request):
    """Minimal ready check - always returns ready"""
    return JsonResponse({"status": "ready"}, status=200)