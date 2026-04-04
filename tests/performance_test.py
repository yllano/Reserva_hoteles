"""
=============================================================
  Sistema de Reserva de Hoteles - Performance Test Suite
  Entrega #1 | Tests: Capacidad, Carga y Estrés
=============================================================
  Uso: python tests/performance_test.py
  Requisito: pip install requests
  Resultado: Un informe JSON se guarda en tests/results/
=============================================================
"""

import requests
import time
import concurrent.futures
import statistics
import json
import os
from datetime import datetime

# --- Configuración ---
GATEWAY_URL = "http://localhost:8000/api"
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

# Endpoints a probar (no requieren autenticación)
ENDPOINTS = {
    "GET /api/hotels":  f"{GATEWAY_URL}/hotels",
    "GET /api/reviews": f"{GATEWAY_URL}/reviews/hotel/test-hotel-id",
}


def make_request(url: str) -> tuple:
    """Realiza una petición GET y retorna (status, latencia)."""
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        latency = time.time() - start
        return response.status_code, latency
    except requests.exceptions.Timeout:
        return "TIMEOUT", 0
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR", 0
    except Exception as e:
        return f"ERROR ({e})", 0


def run_test(test_name: str, concurrency: int, total_requests: int, url: str) -> dict:
    """
    Ejecuta un test de rendimiento con concurrencia definida.
    Retorna un diccionario con los resultados.
    """
    print(f"\n  ▶ {test_name}")
    print(f"    URL: {url}")
    print(f"    Concurrencia: {concurrency} usuarios | Peticiones totales: {total_requests}")

    start_total = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request, url) for _ in range(total_requests)]
        raw_results = [f.result() for f in concurrent.futures.as_completed(futures)]

    total_time = time.time() - start_total

    statuses = [r[0] for r in raw_results]
    latencies = [r[1] for r in raw_results if isinstance(r[0], int) and r[0] < 500]

    success_count = sum(1 for s in statuses if isinstance(s, int) and s < 400)
    error_count = total_requests - success_count
    success_rate = (success_count / total_requests) * 100

    avg_latency = statistics.mean(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    throughput = total_requests / total_time if total_time > 0 else 0

    # Determinar estado del test
    if success_rate == 100:
        test_status = "✅ ESTABLE"
    elif success_rate >= 70:
        test_status = "⚠️  DEGRADADO"
    else:
        test_status = "❌ PUNTO DE QUIEBRE"

    result = {
        "test_name": test_name,
        "endpoint": url,
        "concurrency": concurrency,
        "total_requests": total_requests,
        "success": success_count,
        "errors": error_count,
        "success_rate_pct": round(success_rate, 2),
        "avg_latency_s": round(avg_latency, 4),
        "min_latency_s": round(min_latency, 4),
        "max_latency_s": round(max_latency, 4),
        "total_time_s": round(total_time, 4),
        "throughput_rps": round(throughput, 2),
        "status": test_status,
        "error_distribution": {str(s): statuses.count(s) for s in set(statuses) if s != 200},
    }

    print(f"    Éxito: {success_count}/{total_requests} ({success_rate:.1f}%) | "
          f"Latencia avg: {avg_latency:.4f}s | Throughput: {throughput:.2f} req/s")
    print(f"    Estado: {test_status}")

    return result


def run_all_tests() -> dict:
    """Ejecuta la suite completa de pruebas de rendimiento."""
    all_results = {}
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    for endpoint_name, url in ENDPOINTS.items():
        print(f"\n{'='*60}")
        print(f"  ENDPOINT: {endpoint_name}")
        print(f"{'='*60}")

        tests = [
            # (nombre, concurrencia, total_peticiones)
            ("Prueba de Capacidad (Ligera)",  5,  20),
            ("Prueba de Carga (Moderada)",   20,  50),
            ("Prueba de Estrés (Extrema)",   30,  60),
        ]

        endpoint_results = []
        for test_name, concurrency, total in tests:
            result = run_test(test_name, concurrency, total, url)
            endpoint_results.append(result)
            time.sleep(1)  # Pausa breve entre tests

        all_results[endpoint_name] = endpoint_results

    # Guardar resultados en JSON
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output_path = os.path.join(RESULTS_DIR, f"performance_results_{timestamp}.json")

    report = {
        "generated_at": datetime.now().isoformat(),
        "system": "Sistema de Reserva de Hoteles - Entrega #1",
        "gateway_url": GATEWAY_URL,
        "results": all_results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  ✅ Resultados guardados en:")
    print(f"     {output_path}")
    print(f"{'='*60}\n")

    return report


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  SUITE DE PRUEBAS DE RENDIMIENTO")
    print("  Sistema de Reserva de Hoteles — Entrega #1")
    print("="*60)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Gateway:   {GATEWAY_URL}")
    print("="*60)

    run_all_tests()
