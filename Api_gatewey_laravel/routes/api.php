<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Gateway — Único punto de entrada para todos los microservicios
|--------------------------------------------------------------------------
| Toda petición a los microservicios DEBE pasar por estas rutas.
| El middleware 'auth:sanctum' valida el token Sanctum antes de
| reenviar la solicitud al microservicio correspondiente.
|--------------------------------------------------------------------------
*/

// ─── Rutas públicas: Autenticación (Users MS) ────────────────────────────────
Route::post('/login',           [App\Http\Controllers\AuthController::class, 'login']);
Route::post('/register',        [App\Http\Controllers\AuthController::class, 'register']);
Route::post('/forgot-password', [App\Http\Controllers\AuthController::class, 'forgotPassword']);
Route::post('/reset-password',  [App\Http\Controllers\AuthController::class, 'resetPassword']);

// ─── Rutas protegidas (requieren token Sanctum válido) ────────────────────────
Route::middleware('auth:sanctum')->group(function () {

    // Perfil del usuario autenticado (local, sin proxy)
    Route::get('/user', fn(Request $req) => $req->user());

    // Cerrar sesión
    Route::post('/logout', [App\Http\Controllers\AuthController::class, 'logout']);

    // ── Hoteles MS (http://localhost:8002) ────────────────────────────────────
    Route::prefix('hotels')->group(function () {
        Route::get('/',        [App\Http\Controllers\HotelesController::class, 'index']);
        Route::post('/',       [App\Http\Controllers\HotelesController::class, 'store']);
        Route::get('/{id}',    [App\Http\Controllers\HotelesController::class, 'show']);
        Route::put('/{id}',    [App\Http\Controllers\HotelesController::class, 'update']);
        Route::delete('/{id}', [App\Http\Controllers\HotelesController::class, 'destroy']);
    });

    // ── Reservaciones MS (http://localhost:8003) ──────────────────────────────
    Route::prefix('reservations')->group(function () {
        Route::get('/',           [App\Http\Controllers\ReservasController::class, 'index']);
        Route::post('/',          [App\Http\Controllers\ReservasController::class, 'store']);
        Route::get('/{id}',       [App\Http\Controllers\ReservasController::class, 'show']);
        Route::put('/{id}',       [App\Http\Controllers\ReservasController::class, 'update']);
        Route::delete('/{id}',    [App\Http\Controllers\ReservasController::class, 'destroy']);
        Route::post('/masivo',    [App\Http\Controllers\ReservasController::class, 'cancelarMasivo']);
    });

    // ── Pagos MS (http://localhost:8004) ──────────────────────────────────────
    Route::prefix('payments')->group(function () {
        Route::get('/',        [App\Http\Controllers\PagosController::class, 'index']);
        Route::post('/',       [App\Http\Controllers\PagosController::class, 'store']);
        Route::get('/{id}',    [App\Http\Controllers\PagosController::class, 'show']);
        Route::put('/{id}',    [App\Http\Controllers\PagosController::class, 'update']);
        Route::delete('/{id}', [App\Http\Controllers\PagosController::class, 'destroy']);
    });

    // ── Reseñas MS (http://localhost:8005) ────────────────────────────────────
    Route::prefix('reviews')->group(function () {
        Route::get('/',        [App\Http\Controllers\ResenasController::class, 'index']);
        Route::post('/',       [App\Http\Controllers\ResenasController::class, 'store']);
        Route::get('/{id}',    [App\Http\Controllers\ResenasController::class, 'show']);
        Route::put('/{id}',    [App\Http\Controllers\ResenasController::class, 'update']);
        Route::delete('/{id}', [App\Http\Controllers\ResenasController::class, 'destroy']);
    });
});

// ─── Catch-all: cualquier ruta no definida devuelve 401 ──────────────────────
Route::any('{any}', function () {
    return response()->json([
        'error'   => 'No autenticado',
        'message' => 'Debes autenticarte a través del API Gateway para acceder a este recurso.',
    ], 401);
})->where('any', '.*');
