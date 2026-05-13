import os


GATEWAY_SECRET = os.environ.get('GATEWAY_SECRET', 'gateway-secret-reserva-hoteles-2024')

# Rutas que el gateway llama sin secreto previo (login/register públicos)
# Todas las demás requieren el header X-Gateway-Secret
PUBLIC_PATHS = ['/admin/']


class GatewayAuthMiddleware:
    """
    Middleware que valida que toda petición entrante al microservicio
    proviene del API Gateway mediante el header X-Gateway-Secret.
    Si el header falta o es incorrecto devuelve 401 Unauthorized.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Dejar pasar rutas del admin de Django
        for path in PUBLIC_PATHS:
            if request.path.startswith(path):
                return self.get_response(request)

        secret = request.headers.get('X-Gateway-Secret', '')
        if secret != GATEWAY_SECRET:
            from django.http import JsonResponse
            return JsonResponse(
                {
                    'error': 'Acceso directo no permitido',
                    'message': 'Esta petición debe pasar por el API Gateway en http://localhost:8000/api. No accedas directamente al microservicio.',
                },
                status=401,
            )

        return self.get_response(request)
