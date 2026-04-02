<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ProxyController extends Controller
{
    private $services = [
        'users' => 'http://localhost:8001',
        'hotels' => 'http://localhost:8002',
        'reservations' => 'http://localhost:8003',
        'payments' => 'http://localhost:8004',
        'reviews' => 'http://localhost:8005',
    ];

    public function proxyUsers(Request $request, $any = '') {
        $path = 'api/users' . ($any ? '/' . $any : '');
        return $this->proxy($request, 'users', $path);
    }

    public function proxyHotels(Request $request, $any = '') {
        $path = 'api/hotels' . ($any ? '/' . $any : '');
        return $this->proxy($request, 'hotels', $path);
    }

    public function proxyReservations(Request $request, $any = '') {
        $path = 'api/reservations' . ($any ? '/' . $any : '');
        return $this->proxy($request, 'reservations', $path);
    }

    public function proxyPayments(Request $request, $any = '') {
        $path = 'api/payments' . ($any ? '/' . $any : '');
        return $this->proxy($request, 'payments', $path);
    }

    public function proxyReviews(Request $request, $any = '') {
        $path = 'api/reviews' . ($any ? '/' . $any : '');
        return $this->proxy($request, 'reviews', $path);
    }

    private function proxy(Request $request, $service, $path)
    {
        if (!isset($this->services[$service])) {
            return response()->json(['error' => 'Service not found'], 404);
        }

        $url = $this->services[$service] . '/' . $path;
        $method = $request->method();
        $headers = $request->headers->all();
        $body = $request->all();

        // Remove host header to avoid conflicts
        unset($headers['host']);

        try {
            $response = Http::withHeaders($headers)
                ->send($method, $url, [
                    'json' => $body,
                    'query' => $request->query()
                ]);

            return response()->json($response->json(), $response->status());
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Service Unavailable',
                'message' => $e->getMessage(),
                'url' => $url
            ], 503);
        }
    }
}
