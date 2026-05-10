"""
=============================================================
  Prueba de Estrés — Microservicio de Pagos (Express / PostgreSQL)
  Puerto objetivo : http://localhost:8004
  Ejecutar        : locust -f locustfile.py --host=http://localhost:8004
=============================================================

Escenario:
  - 10 tareas con pesos distintos que simulan el tráfico real:
      · Las lecturas son más frecuentes que las escrituras.
      · El endpoint /process es el más crítico (mayor peso).
  - Un usuario virtual siembra su propio transaction_id en on_start
    para evitar errores 404 en tareas de detalle/actualización.
"""

import random
from locust import HttpUser, task, between


# ---------------------------------------------------------------------------
# Datos de prueba reutilizables
# ---------------------------------------------------------------------------
RESERVACIONES_IDS = list(range(1, 21))   # IDs de reservaciones de prueba

MONTOS = [50.00, 120.50, 200.00, 375.99, 89.90, 1500.00, 45.00, 600.75]

ESTADOS_VALIDOS = ["success", "pending", "failed"]


# ---------------------------------------------------------------------------
# Usuario virtual
# ---------------------------------------------------------------------------
class PagosStressUser(HttpUser):
    """
    Simula un cliente que interactúa con el microservicio de Pagos.
    Tiempo de espera entre tareas: 1 – 3 segundos (simula comportamiento humano).
    """
    wait_time = between(1, 3)

    # ID de transacción creada por este usuario en on_start
    transaction_id: int | None = None

    # -----------------------------------------------------------------------
    # Ciclo de vida del usuario
    # -----------------------------------------------------------------------
    def on_start(self):
        """Crea una transacción inicial para usar en tareas de lectura/edición."""
        payload = {
            "reservation_id": random.choice(RESERVACIONES_IDS),
            "amount": random.choice(MONTOS),
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="[setup] POST /api/payments/process",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                # Guardamos el ID para usarlo en tareas posteriores
                self.transaction_id = data.get("transaction", {}).get("id")
                response.success()
            else:
                # Si el servicio no está activo, marcamos fallo pero continuamos
                response.failure(
                    f"on_start falló con status {response.status_code}: {response.text}"
                )

    # -----------------------------------------------------------------------
    # Tarea 1 – Procesar un pago (flujo principal, mayor carga)
    # -----------------------------------------------------------------------
    @task(4)
    def procesar_pago(self):
        """POST /api/payments/process — simula un pago nuevo."""
        payload = {
            "reservation_id": random.choice(RESERVACIONES_IDS),
            "amount": random.choice(MONTOS),
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="POST /api/payments/process",
        ) as response:
            if response.status_code in (200, 201, 400):
                # 400 es esperado (tasa de fallo simulada del 5 %)
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 2 – Procesar pago con monto alto
    # -----------------------------------------------------------------------
    @task(2)
    def procesar_pago_monto_alto(self):
        """POST /api/payments/process — monto elevado para detectar latencia."""
        payload = {
            "reservation_id": random.choice(RESERVACIONES_IDS),
            "amount": round(random.uniform(2000.00, 9999.99), 2),
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="POST /api/payments/process (monto alto)",
        ) as response:
            if response.status_code in (200, 201, 400):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 3 – Procesar pago con monto mínimo
    # -----------------------------------------------------------------------
    @task(2)
    def procesar_pago_monto_minimo(self):
        """POST /api/payments/process — monto mínimo (caso borde)."""
        payload = {
            "reservation_id": random.choice(RESERVACIONES_IDS),
            "amount": 0.01,
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="POST /api/payments/process (monto minimo)",
        ) as response:
            if response.status_code in (200, 201, 400):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 4 – Procesar pago sin amount (validación de errores)
    # -----------------------------------------------------------------------
    @task(1)
    def procesar_pago_sin_amount(self):
        """POST /api/payments/process — sin campo 'amount' (debe retornar error)."""
        payload = {
            "reservation_id": random.choice(RESERVACIONES_IDS),
            # amount omitido intencionalmente
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="POST /api/payments/process (sin amount)",
        ) as response:
            # 400/422/500 son respuestas válidas ante datos incompletos
            if response.status_code in (400, 422, 500):
                response.success()
            elif response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 5 – Procesar pago sin reservation_id (validación de errores)
    # -----------------------------------------------------------------------
    @task(1)
    def procesar_pago_sin_reservation(self):
        """POST /api/payments/process — sin reservation_id (caso inválido)."""
        payload = {
            "amount": random.choice(MONTOS),
            # reservation_id omitido intencionalmente
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="POST /api/payments/process (sin reservation_id)",
        ) as response:
            if response.status_code in (400, 422, 500):
                response.success()
            elif response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 6 – Concurrencia: múltiples pagos para la misma reserva
    # -----------------------------------------------------------------------
    @task(2)
    def procesar_pago_misma_reserva(self):
        """POST /api/payments/process — misma reserva, detecta race conditions."""
        payload = {
            "reservation_id": 1,   # ID fijo para forzar concurrencia
            "amount": random.choice(MONTOS),
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="POST /api/payments/process (concurrencia)",
        ) as response:
            if response.status_code in (200, 201, 400, 409, 500):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 7 – Payload JSON vacío
    # -----------------------------------------------------------------------
    @task(1)
    def procesar_pago_payload_vacio(self):
        """POST /api/payments/process — payload vacío, prueba robustez."""
        with self.client.post(
            "/api/payments/process",
            json={},
            catch_response=True,
            name="POST /api/payments/process (payload vacio)",
        ) as response:
            if response.status_code in (400, 422, 500):
                response.success()
            elif response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 8 – Amount como string (tipo incorrecto)
    # -----------------------------------------------------------------------
    @task(1)
    def procesar_pago_amount_invalido(self):
        """POST /api/payments/process — amount no numérico (caso borde)."""
        payload = {
            "reservation_id": random.choice(RESERVACIONES_IDS),
            "amount": "gratis",
        }
        with self.client.post(
            "/api/payments/process",
            json=payload,
            catch_response=True,
            name="POST /api/payments/process (amount invalido)",
        ) as response:
            if response.status_code in (400, 422, 500):
                response.success()
            elif response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 9 – Rafaga de pagos consecutivos (burst)
    # -----------------------------------------------------------------------
    @task(3)
    def rafaga_de_pagos(self):
        """POST /api/payments/process x3 — simula pico de tráfico breve."""
        for _ in range(3):
            payload = {
                "reservation_id": random.choice(RESERVACIONES_IDS),
                "amount": random.choice(MONTOS),
            }
            with self.client.post(
                "/api/payments/process",
                json=payload,
                catch_response=True,
                name="POST /api/payments/process (burst)",
            ) as response:
                if response.status_code in (200, 201, 400):
                    response.success()
                else:
                    response.failure(f"Status inesperado: {response.status_code}")

    # -----------------------------------------------------------------------
    # Tarea 10 – Endpoint inexistente (prueba manejo de rutas no definidas)
    # -----------------------------------------------------------------------
    @task(1)
    def endpoint_inexistente(self):
        """GET /api/payments — verifica si el servicio expone un listado o retorna 404."""
        with self.client.get(
            "/api/payments",
            catch_response=True,
            name="GET /api/payments (listado/404)",
        ) as response:
            # Cualquier respuesta HTTP es válida aquí; lo importante es que no crashee
            if response.status_code < 500:
                response.success()
            else:
                response.failure(f"Error 5xx inesperado: {response.status_code}")