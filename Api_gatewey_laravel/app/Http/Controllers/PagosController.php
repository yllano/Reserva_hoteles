<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class PagosController extends Controller
{
    private $url;

    public function __construct()
    {
        $this->url = env('PAYMENTS_SERVICE_URL', 'http://localhost:8004') . '/api/payments';
    }

    /**
     * Listar pagos del usuario autenticado.
     */
    public function index(Request $request)
    {
        $res = Http::withToken($request->bearerToken())
            ->get($this->url, array_merge(
                $request->query(),
                ['user_id' => auth()->id()]
            ));

        return response()->json($res->json(), $res->status());
    }

    /**
     * Obtener un pago por ID.
     */
    public function show(Request $request, $id)
    {
        $res = Http::withToken($request->bearerToken())
            ->get("{$this->url}/{$id}", ['user_id' => auth()->id()]);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Registrar un nuevo pago.
     */
    public function store(Request $request)
    {
        $data = $request->all();
        $data['user_id'] = auth()->id();

        $res = Http::withToken($request->bearerToken())
            ->post($this->url, $data);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Actualizar un pago (ej. cambiar estado).
     */
    public function update(Request $request, $id)
    {
        $data = $request->all();
        $data['user_id'] = auth()->id();

        $res = Http::withToken($request->bearerToken())
            ->put("{$this->url}/{$id}", $data);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Eliminar / revertir un pago.
     */
    public function destroy(Request $request, $id)
    {
        $res = Http::withToken($request->bearerToken())
            ->delete("{$this->url}/{$id}", ['user_id' => auth()->id()]);

        return response()->json($res->json(), $res->status());
    }
}
