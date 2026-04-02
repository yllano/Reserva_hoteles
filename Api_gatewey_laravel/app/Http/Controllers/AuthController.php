<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{
    private $userServiceUrl = 'http://localhost:8001/api/users';

    public function register(Request $request)
    {
        $response = Http::post($this->userServiceUrl . '/register/', $request->all());

        if ($response->successful()) {
            // Also create a local user record in Laravel for token mapping (Sanctum needs a model)
            $userData = $response->json();
            
            // Check if user already exists locally by email
            $user = User::updateOrCreate(
                ['email' => $userData['email']],
                [
                    'name' => $userData['username'],
                    'password' => Hash::make($request->password), // Laravel needs a pass, but we use Django's auth
                ]
            );

            return response()->json([
                'message' => 'User registered successfully',
                'user' => $userData
            ], 201);
        }

        return response()->json($response->json(), $response->status());
    }

    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        // Validate credentials against Django User MS
        $response = Http::post($this->userServiceUrl . '/login/', [
            'email' => $request->email,
            'password' => $request->password,
        ]);

        if ($response->successful()) {
            $userData = $response->json();
            
            // Ensure user exists locally for Sanctum
            $user = User::where('email', $request->email)->first();
            
            if (!$user) {
                // Should exist if registered through gateway, but creating if missing
                $user = User::create([
                    'name' => $userData['user']['username'] ?? $request->email,
                    'email' => $request->email,
                    'password' => Hash::make($request->password),
                ]);
            }

            $token = $user->createToken('auth_token')->plainTextToken;

            return response()->json([
                'access_token' => $token,
                'token_type' => 'Bearer',
                'user_id' => $userData['user']['id'],
            ]);
        }

        return response()->json(['message' => 'Invalid login credentials'], 401);
    }

    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();

        return response()->json(['message' => 'Logged out successfully']);
    }

    public function forgotPassword(Request $request)
    {
        $response = Http::post($this->userServiceUrl . '/forgot-password/', $request->all());
        return response()->json($response->json(), $response->status());
    }

    public function resetPassword(Request $request)
    {
        $response = Http::post($this->userServiceUrl . '/reset-password/', $request->all());
        return response()->json($response->json(), $response->status());
    }
}
