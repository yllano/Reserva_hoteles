<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use App\Http\Controllers\Concerns\ForwardsToMicroservice;

class ReservasController extends Controller
{
    use ForwardsToMicroservice;
    private $url;

    public function __construct()
    {
        $this->url = config('services.reservations.url', 'http://localhost:8003') . '/api/reservations';
    }

    /**
     * Listar reservas del usuario autenticado.
     */
    public function index(Request $request)
    {
        $userId = auth()->id();
        $res = $this->gatewayHttp()->withToken($request->bearerToken())
            ->get("{$this->url}/user/{$userId}");

        return response()->json($res->json(), $res->status());
    }

    /**
     * Obtener una reserva por ID.
     */
    public function show(Request $request, $id)
    {
        $res = $this->gatewayHttp()->withToken($request->bearerToken())
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

        $res = $this->gatewayHttp()->withToken($request->bearerToken())
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

        $res = $this->gatewayHttp()->withToken($request->bearerToken())
            ->put("{$this->url}/{$id}", $data);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Cancelar (eliminar) una reserva.
     */
    public function destroy(Request $request, $id)
    {
        $res = $this->gatewayHttp()->withToken($request->bearerToken())
            ->delete("{$this->url}/{$id}", ['user_id' => auth()->id()]);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Cancelar múltiples reservas de forma masiva.
     */
    public function cancelarMasivo(Request $request)
    {
        $res = $this->gatewayHttp()->withToken($request->bearerToken())
            ->post("{$this->url}/masivo", [
                'ids'     => $request->ids,
                'user_id' => auth()->id(),
            ]);

        return response()->json($res->json(), $res->status());
    }
}
