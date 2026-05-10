<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

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

        // Siempre responder con JSON ante peticiones no autenticadas (sin redirect)
        $middleware->redirectGuestsTo(fn() => response()->json([
            'error'   => 'No autenticado',
            'message' => 'Debes autenticarte a través del API Gateway para acceder a este recurso.',
        ], 401));
    })

    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
