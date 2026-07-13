# Guía General de Servicios AWS

Esta guía proporciona una descripción detallada de cada uno de los servicios de AWS que componen la infraestructura del proyecto **cleanmybelly**. Esta arquitectura está diseñada para ser completamente **serverless**, lo que garantiza alta disponibilidad, escalabilidad automática y costos mínimos de mantenimiento.

---

## Listado de Servicios

### 1. Amazon Route 53
*   **Propósito**: Servicio de Sistema de Nombres de Dominio (DNS) altamente disponible y escalable.
*   **Función en el proyecto**: Traduce el dominio personalizado (ej. `cleanmybelly.com`) en las direcciones IP y endpoints de los recursos correspondientes en AWS, enrutando al usuario final a CloudFront (para el Frontend) o a API Gateway (para el Backend).

### 2. AWS Certificate Manager (ACM)
*   **Propósito**: Emisión y gestión de certificados de Capa de Sockets Seguros (SSL/TLS).
*   **Función en el proyecto**: Provee certificados SSL gratuitos y autorenovables para habilitar conexiones HTTPS seguras en el dominio principal y subdominios del proyecto.

### 3. Amazon S3 (Simple Storage Service)
*   **Propósito**: Almacenamiento de objetos diseñado para almacenar cualquier cantidad de datos con alta durabilidad.
*   **Función en el proyecto**: Actúa como hosting del frontend del sitio web. Almacena todos los archivos estáticos compilados (HTML, CSS, JS, imágenes).

### 4. Amazon CloudFront
*   **Propósito**: Red de entrega de contenido (CDN) global rápida y segura.
*   **Función en el proyecto**: Distribuye el frontend a nivel global con latencia mínima, almacena en caché las respuestas y sirve el contenido directamente desde las ubicaciones de borde (Edge Locations) de AWS, reduciendo la carga directa sobre el bucket de S3.

### 5. Amazon API Gateway
*   **Propósito**: Servicio administrado que facilita a los desarrolladores la creación, publicación, mantenimiento, monitoreo y seguridad de APIs a cualquier escala.
*   **Función en el proyecto**: Punto de entrada único para el backend. Recibe peticiones HTTP seguras desde el frontend y las redirige hacia la función Lambda correspondiente.

### 6. AWS Lambda
*   **Propósito**: Servicio de cómputo serverless que permite ejecutar código sin aprovisionar ni administrar servidores.
*   **Función en el proyecto**: Ejecuta la lógica de negocio necesaria de forma reactiva (por ejemplo, validar números de teléfono y asignar códigos promocionales) cuando recibe eventos desde API Gateway.

### 7. Amazon DynamoDB
*   **Propósito**: Base de datos NoSQL completamente administrada de clave-valor y documentos que ofrece un rendimiento rápido en milisegundos de un solo dígito a cualquier escala.
*   **Función en el proyecto**: Almacena de forma persistente los registros de números de teléfono y sus respectivos cupones. Funciona en modo *On-Demand* para escalar automáticamente según la demanda de los usuarios.

### 8. AWS IAM (Identity and Access Management)
*   **Propósito**: Control seguro del acceso a los servicios y recursos de AWS.
*   **Función en el proyecto**: Define políticas y roles específicos de ejecución con el principio de menor privilegio (por ejemplo, permitiendo que únicamente la función Lambda tenga autorización para escribir en la tabla de DynamoDB).

### 9. Amazon CloudWatch
*   **Propósito**: Servicio de monitoreo y observabilidad de recursos.
*   **Función en el proyecto**: Recopila métricas y centraliza los logs de ejecución (`console.log`, errores y trazas) generados por AWS Lambda para auditorías, alertas y depuración rápida.
