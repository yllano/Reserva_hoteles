# Informe de Pruebas de Rendimiento — Entrega #1

> **Sistema**: Sistema de Reserva de Hoteles  
> **Script**: `tests/performance_test.py` (automatizado)  
> **Resultados JSON**: `tests/results/performance_results_<timestamp>.json`

---

## 1. Metodología

Las pruebas fueron realizadas con un script Python automatizado (`tests/performance_test.py`) usando `ThreadPoolExecutor` para simular usuarios concurrentes reales. El script ejecuta tres tipos de prueba en secuencia sobre cada endpoint y exporta un archivo JSON con métricas detalladas.

**Endpoints evaluados**:
- `GET /api/hotels` — listado de hoteles vía API Gateway
- `GET /api/reviews/hotel/:id` — reseñas de un hotel vía API Gateway

**Métricas capturadas por prueba**:
- Tasa de éxito (%)
- Latencia promedio, mínima y máxima (segundos)
- Throughput (peticiones por segundo)
- Distribución de errores

---

## 2. Resultados

### 2.1 Prueba de Capacidad (Carga Ligera)

**Objetivo**: Verificar el rendimiento óptimo del sistema bajo una carga mínima.

| Parámetro | Valor |
|---|---|
| Usuarios concurrentes | 5 |
| Peticiones totales | 20 |
| Tasa de éxito | 100% |
| Latencia promedio | ~0.15 s |
| Throughput | ~12 req/s |
| Estado | ✅ ESTABLE |

**Observación**: Con 5 usuarios concurrentes el sistema responde sin degradación. El API Gateway Laravel procesa las peticiones sin generar colas de espera.

---

### 2.2 Prueba de Carga (Tráfico Moderado)

**Objetivo**: Evaluar el comportamiento bajo tráfico sostenido realista.

| Parámetro | Valor |
|---|---|
| Usuarios concurrentes | 20 |
| Peticiones totales | 50 |
| Tasa de éxito | 100% |
| Latencia promedio | ~0.85 s |
| Throughput | ~8 req/s |
| Estado | ⚠️ DEGRADADO |

**Observación**: El sistema mantiene el 100% de éxito pero la latencia sube considerablemente. El cuello de botella identificado es el servidor de desarrollo de Laravel (`php artisan serve`), que procesa peticiones de forma secuencial (single-process). Los microservicios Express y Flask responden correctamente una vez que el Gateway les delega la petición.

---

### 2.3 Prueba de Estrés (Carga Extrema)

**Objetivo**: Identificar el punto de quiebre del sistema.

| Parámetro | Valor |
|---|---|
| Usuarios concurrentes | 30 |
| Peticiones totales | 60 |
| Tasa de éxito | ~40% |
| Latencia promedio | >5.0 s |
| Throughput | ~3 req/s |
| Estado | ❌ PUNTO DE QUIEBRE |

**Observación**: Con más de 30 usuarios concurrentes el servidor PHP built-in agota su capacidad de encolamiento, provocando que las peticiones fallen por timeout o `Connection refused`. Los errores son originados exclusivamente en el Gateway y no en los microservicios internos.

---

## 3. Resumen Comparativo

| Tipo de Prueba | Concurrencia | Éxito | Latencia avg | Estado |
|---|---|---|---|---|
| Capacidad | 5 | 100% | ~0.15 s | ✅ Estable |
| Carga | 20 | 100% | ~0.85 s | ⚠️ Degradado |
| Estrés | 30+ | ~40% | >5.0 s | ❌ Punto de quiebre |

---

## 4. Conclusiones y Recomendaciones

1. **Cuello de Botella Principal**: El servidor web de desarrollo PHP (`php artisan serve`) es single-process y no apto para cargas concurrentes. Es el único punto de falla del sistema actual.

2. **Resiliencia de Microservicios**: Express (Node.js) y Flask (Python) demostraron alta resiliencia. Cuando el Gateway les entrega la petición, la procesan y responden sin errores.

3. **Solución Proyectada (Entrega #2)**: Desplegar el Gateway con **Nginx + PHP-FPM** en contenedores Docker para habilitar el procesamiento paralelo de peticiones. Se estima que esto multiplicará por 10x la capacidad bajo carga moderada.

4. **Reproducibilidad**: Para repetir las pruebas, ejecutar:
   ```bash
   python tests/performance_test.py
   ```
   Los resultados se guardan automáticamente en `tests/results/`.
