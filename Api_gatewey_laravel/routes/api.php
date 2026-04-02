<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Auth Routes (Proxied to Users MS)
Route::post('/login', [App\Http\Controllers\AuthController::class, 'login']);
Route::post('/register', [App\Http\Controllers\AuthController::class, 'register']);
Route::post('/logout', [App\Http\Controllers\AuthController::class, 'logout'])->middleware('auth:sanctum');

// Gateway Proxy Routes
Route::any('/hotels/{any?}', [App\Http\Controllers\ProxyController::class, 'proxyHotels'])->where('any', '.*');
Route::any('/users/{any?}', [App\Http\Controllers\ProxyController::class, 'proxyUsers'])->where('any', '.*');
Route::any('/reservations/{any?}', [App\Http\Controllers\ProxyController::class, 'proxyReservations'])->where('any', '.*')->middleware('auth:sanctum');
Route::any('/payments/{any?}', [App\Http\Controllers\ProxyController::class, 'proxyPayments'])->where('any', '.*')->middleware('auth:sanctum');
Route::any('/reviews/{any?}', [App\Http\Controllers\ProxyController::class, 'proxyReviews'])->where('any', '.*');
