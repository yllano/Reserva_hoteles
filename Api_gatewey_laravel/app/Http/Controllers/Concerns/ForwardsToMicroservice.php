<?php

namespace App\Http\Controllers\Concerns;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

/**
 * Trait compartido por todos los controllers del gateway.
 * Añade automáticamente el header X-Gateway-Secret en cada petición
 * que se reenvía a un microservicio.
 */
trait ForwardsToMicroservice
{
    /**
     * Construye una instancia Http con el header secreto del gateway ya incluido.
     */
    protected function gatewayHttp(): \Illuminate\Http\Client\PendingRequest
    {
        return Http::timeout(10)->withHeaders([
            'X-Gateway-Secret' => config('services.gateway_secret'),
        ]);
    }
}
