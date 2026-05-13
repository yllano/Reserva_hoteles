<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use App\Http\Controllers\Concerns\ForwardsToMicroservice;

class ResenasController extends Controller
{
    use ForwardsToMicroservice;
    private $url;

    public function __construct()
    {
        $this->url = config('services.reviews.url', 'http://localhost:8005') . '/api/reviews';
    }

    /**
     * Listar reseñas (filtradas opcionalmente por hotel o usuario).
     */
    public function index(Request $request)
    {
        $res = $this->gatewayHttp()->withToken($request->bearerToken())
            ->get($this->url, array_merge(
                $request->query(),
                ['user_id' => auth()->id()]
            ));

        return response()->json($res->json(), $res->status());
    }

    /**
     * Obtener una reseña por ID.
     */
    public function show(Request $request, $id)
    {
        $res = $this->gatewayHttp()->withToken($request->bearerToken())
            ->get("{$this->url}/{$id}", ['user_id' => auth()->id()]);

        return response()->json($res->json(), $res->status());
    }

    /**
     * Publicar una nueva reseña.
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
     * Actualizar una reseña existente.
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
     * Eliminar una reseña.
     */
    public function destroy(Request $request, $id)
    {
        $res = $this->gatewayHttp()->withToken($request->bearerToken())
            ->delete("{$this->url}/{$id}", ['user_id' => auth()->id()]);

        return response()->json($res->json(), $res->status());
    }
}
