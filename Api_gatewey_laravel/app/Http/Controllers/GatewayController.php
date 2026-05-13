<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class GatewayController extends Controller
{
    private $services;
    private $secret;

    public function __construct()
    {
        $this->services = [
            'users'        => config('services.users.url',        'http://localhost:8001'),
            'hotels'       => config('services.hotels.url',       'http://localhost:8002'),
            'reservations' => config('services.reservations.url', 'http://localhost:8003'),
            'payments'     => config('services.payments.url',     'http://localhost:8004'),
            'reviews'      => config('services.reviews.url',      'http://localhost:8005'),
        ];
        $this->secret = config('services.gateway_secret');
    }

    public function forwardUsers(Request $request, $any = '') {
        $path = 'api/users' . ($any ? '/' . $any : '');
        return $this->forward($request, 'users', $path);
    }

    public function forwardHotels(Request $request, $any = '') {
        $path = 'api/hotels' . ($any ? '/' . $any : '');
        return $this->forward($request, 'hotels', $path);
    }

    public function forwardReservations(Request $request, $any = '') {
        $path = 'api/reservations' . ($any ? '/' . $any : '');
        return $this->forward($request, 'reservations', $path);
    }

    public function forwardPayments(Request $request, $any = '') {
        $path = 'api/payments' . ($any ? '/' . $any : '');
        return $this->forward($request, 'payments', $path);
    }

    public function forwardReviews(Request $request, $any = '') {
        $path = 'api/reviews' . ($any ? '/' . $any : '');
        return $this->forward($request, 'reviews', $path);
    }

    private function forward(Request $request, $service, $path)
    {
        if (!isset($this->services[$service])) {
            return response()->json(['error' => 'Servicio no encontrado'], 404);
        }

        $url     = $this->services[$service] . '/' . $path;
        $method  = $request->method();
        $headers = $request->headers->all();
        $body    = $request->all();

        // Evitar conflicto de cabecera host
        unset($headers['host']);

        // Inyectar el secreto interno para que el microservicio verifique que viene del gateway
        $headers['X-Gateway-Secret'] = [$this->secret];

        try {
            $response = Http::withHeaders($headers)
                ->send($method, $url, [
                    'json'  => $body,
                    'query' => $request->query(),
                ]);

            return response()->json($response->json(), $response->status());
        } catch (\Exception $e) {
            return response()->json([
                'error'   => 'Servicio no disponible',
                'message' => $e->getMessage(),
                'url'     => $url,
            ], 503);
        }
    }
}
