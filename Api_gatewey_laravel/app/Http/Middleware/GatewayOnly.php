<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/**
 * GatewayOnly — rechaza cualquier petición que no provenga
 * de un cliente autenticado a través del API Gateway (Sanctum).
 *
 * Uso: aplícalo en las rutas de los microservicios internos
 * o en el propio gateway para forzar que todo pase por él.
 */
class GatewayOnly
{
    public function handle(Request $request, Closure $next): Response
    {
        // Si el usuario NO está autenticado vía Sanctum → 401
        if (!auth('sanctum')->check()) {
            return response()->json([
                'error'   => 'No autenticado',
                'message' => 'Debes autenticarte a través del API Gateway para acceder a este recurso.',
            ], 401);
        }

        return $next($request);
    }
}
