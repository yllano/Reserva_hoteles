# Diagrama de Arquitectura - Sistema de Reserva de Hoteles

Este diagrama ilustra la arquitectura de microservicios, el API Gateway como único punto de entrada y los diversos sistemas de bases de datos utilizados en los servicios.

```mermaid
graph TD
    Client["Cliente / Usuario"] --> Gateway["API Gateway (Laravel)"]
    
    subgraph Microservicios
        Gateway --> Users["Users MS (Django)"]
        Gateway --> Hotels["Hotels MS (Express)"]
        Gateway --> Reservas["Reservations MS (Flask)"]
        Gateway --> Pagos["Payments MS (Express)"]
        Gateway --> Resenas["Reviews MS (Flask)"]
    end
    
    subgraph Bases_de_Datos
        Users --> PG1[("PostgreSQL (users_db)")]
        Pagos --> PG2[("PostgreSQL (pagos_db)")]
        Reservas --> MySQL1[("MySQL (reserva_hotel)")]
        Gateway --> MySQL2[("MySQL (reserva_hotel)")]
        Hotels --> Firestore[("Cloud Firestore")]
        Resenas --> Firestore
    end
    
    style Gateway fill:#f9f,stroke:#333,stroke-width:2px
    style Users fill:#bbf,stroke:#333,stroke-width:1px
    style Hotels fill:#bfb,stroke:#333,stroke-width:1px
    style Reservas fill:#fbb,stroke:#333,stroke-width:1px
    style Pagos fill:#ffb,stroke:#333,stroke-width:1px
    style Resenas fill:#bff,stroke:#333,stroke-width:1px
```

## Flujo de Comunicación
1. **Petición**: Todas las peticiones externas llegan al API Gateway construido en Laravel.
2. **Autenticación**: El Gateway utiliza Sanctum y se comunica con el microservicio de Usuarios (Django) para validar credenciales.
3. **Proxy**: Las peticiones validadas se redirigen al microservicio correspondiente según la ruta de la URL.
4. **Gestión de Datos**: Cada microservicio gestiona su propia base de datos, siguiendo estrictamente el patrón de una base de datos por servicio.
