<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ReservasController extends Controller
{
    private $url;

    public function __construct()
    {
        $this->url = env('RESERVATIONS_SERVICE_URL', 'http://localhost:8003') . '/api/reservations';
    }

    /**
     * Listar reservas del usuario autenticado.
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
     * Obtener una reserva por ID.
     */
    public function show(Request $request, $id)
    {
        $res = Http::withToken($request->bearerToken())
            ->get("{$this->url}/{$id}", ['user_id' => auth()->id()]);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Crear una nueva reserva.
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
     * Actualizar una reserva existente.
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
     * Cancelar (eliminar) una reserva.
     */
    public function destroy(Request $request, $id)
    {
        $res = Http::withToken($request->bearerToken())
            ->delete("{$this->url}/{$id}", ['user_id' => auth()->id()]);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Cancelar múltiples reservas de forma masiva.
     */
    public function cancelarMasivo(Request $request)
    {
        $res = Http::withToken($request->bearerToken())
            ->post("{$this->url}/masivo", [
                'ids'     => $request->ids,
                'user_id' => auth()->id(),
            ]);

        return response()->json($res->json(), $res->status());
    }
}
