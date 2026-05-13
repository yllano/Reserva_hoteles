<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Mailgun, Postmark, AWS and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'key' => env('POSTMARK_API_KEY'),
    ],

    'resend' => [
        'key' => env('RESEND_API_KEY'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    'users' => [
        'url' => env('USERS_SERVICE_URL', 'http://localhost:8001'),
    ],

    'hotels' => [
        'url' => env('HOTELS_SERVICE_URL', 'http://localhost:8002'),
    ],

    'reservations' => [
        'url' => env('RESERVATIONS_SERVICE_URL', 'http://localhost:8003'),
    ],

    'payments' => [
        'url' => env('PAYMENTS_SERVICE_URL', 'http://localhost:8004'),
    ],

    'reviews' => [
        'url' => env('REVIEWS_SERVICE_URL', 'http://localhost:8005'),
    ],

    // Secreto interno compartido entre el Gateway y todos los microservicios
    'gateway_secret' => env('GATEWAY_SECRET', 'gateway-secret-reserva-hoteles-2024'),

];
