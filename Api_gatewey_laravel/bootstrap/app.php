<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Auth\AuthenticationException;
use Illuminate\Http\Request;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // Alias para el middleware de gateway
        $middleware->alias([
            'gateway' => \App\Http\Middleware\GatewayOnly::class,
        ]);
    })

    ->withExceptions(function (Exceptions $exceptions): void {
        // Siempre responder con JSON cuando un usuario no está autenticado (API Gateway)
        $exceptions->render(function (AuthenticationException $e, Request $request) {
            return response()->json([
                'error'   => 'No autenticado',
                'message' => 'Debes autenticarte a través del API Gateway para acceder a este recurso.',
            ], 401);
        });
    })->create();
