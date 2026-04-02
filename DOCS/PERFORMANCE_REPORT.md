# Informe de Pruebas de Rendimiento - Entrega #1

Este documento detalla los resultados de las pruebas de rendimiento realizadas sobre el API Gateway y los microservicios internos del sistema de reserva de hoteles.

## 1. Metodología
Se utilizó un script de Python (`tests/performance_test.py`) que usa `ThreadPoolExecutor` para simular múltiples usuarios concurrentes realizando peticiones `GET` al endpoint de hoteles a través del API Gateway.

## 2. Pruebas de Capacidad
**Objetivo**: Determinar el rendimiento óptimo del sistema con una carga ligera.
- **Usuarios Concurrentes**: 5
- **Peticiones Totales**: 20
- **Resultado**: 
    - Éxito: 100%
    - Latencia Promedio: ~0.15s
    - Estado: **Estable**

## 3. Pruebas de Carga
**Objetivo**: Evaluar el comportamiento bajo un tráfico moderado de usuarios.
- **Usuarios Concurrentes**: 20
- **Peticiones Totales**: 50
- **Resultado**:
    - Éxito: 100%
    - Latencia Promedio: ~0.85s
    - Observación: Se empieza a notar una degradación en el tiempo de respuesta debido a que el servidor de desarrollo de Laravel (`artisan serve`) procesa peticiones de forma secuencial.

## 4. Pruebas de Estrés
**Objetivo**: Identificar el punto de quiebre del sistema.
- **Usuarios Concurrentes**: 30+
- **Peticiones Totales**: 50+
- **Resultado**:
    - Éxito: 40% (Errores de Timeout / Conexión rehusada)
    - Latencia Promedio: >5.0s
    - **Punto de Quiebre**: Con más de 30 usuarios concurrentes, el servidor `php artisan serve` agota su capacidad de encolamiento, provocando que las peticiones queden en espera (hang) o fallen.

## 5. Conclusiones y Recomendaciones
1. **Cuello de Botella**: El principal limitante detectado es el servidor web de desarrollo (PHP Built-in server). 
2. **Solución Proyectada**: Para el despliegue final (Entrega #2 y #3), se recomienda el uso de **Docker** con **Nginx** y **PHP-FPM** para permitir el procesamiento paralelo de peticiones.
3. **Escalabilidad**: Los microservicios de Node.js (Express) y Python (Flask) demostraron una resiliencia superior, respondiendo correctamente una vez que el Gateway les entregaba la petición.
