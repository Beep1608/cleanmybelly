# Delegación de Dominio: Namecheap a AWS Route 53 (Proceso Desacoplado)

Este manual explica cómo delegar tu dominio comprado en **Namecheap** a **AWS Route 53** utilizando servidores de nombres (NS). 

Debido a que la validación de certificados SSL (ACM) requiere que el dominio ya resuelva correctamente hacia AWS, **esta infraestructura de red se debe desplegar por partes**.

---

## Secuencia de Ejecución

El proceso se divide en 4 fases secuenciales:

```
[Fase 1: Crear Zona DNS] 
       │
       ▼
[Fase 2: Obtener Name Servers (Outputs)] 
       │
       ▼
[Fase 3: Delegar en Namecheap] 
       │
       ▼
[Fase 4: Crear y Validar Certificados SSL]
```

---

## Paso 1: Crear la Zona DNS en Route 53

El primer paso es crear el contenedor DNS en AWS (Hosted Zone). Esto generará los servidores de nombres específicos para tu dominio.

1. Ve a la carpeta de la zona DNS:
   ```bash
   cd aws/infra/shared/networking/dns-zone
   ```
2. Inicializa Terraform y ejecuta el despliegue:
   ```bash
   terraform init
   terraform apply
   ```

---

## Paso 2: Obtener las variables de salida (Name Servers)

Una vez que el despliegue de la Fase 1 termine, Terraform mostrará en la consola las variables de salida (*outputs*). También puedes consultarlas en cualquier momento ejecutando:

```bash
terraform output
```

Verás una salida similar a esta:
```hcl
hosted_zone_id   = "Z0123456789ABCDEF"
hosted_zone_name = "cleanmybelly.com"
name_servers     = [
  "ns-1025.awsdns-00.org",
  "ns-154.awsdns-19.com",
  "ns-782.awsdns-33.net",
  "ns-1981.awsdns-56.co.uk"
]
```

**Copia las 4 direcciones** de la lista `name_servers` (sin comillas ni comas). Las necesitarás para el siguiente paso.

---

## Paso 3: Configurar Custom DNS en Namecheap (Consola 2026)

Con las 4 direcciones de AWS Name Servers, actualiza tu dominio en la plataforma de Namecheap:

1. Inicia sesión en tu cuenta de [Namecheap.com](https://www.namecheap.com/).
2. En el menú lateral izquierdo, haz clic en **Domain List** (Lista de Dominios).
3. Busca tu dominio (ej. `cleanmybelly.com`) y haz clic en el botón **Manage** (Administrar) a la derecha.
4. Desplázate hacia abajo hasta la sección **NAMESERVERS** (Servidores de nombres).
5. Cambia la opción del menú desplegable (que por defecto dice *Namecheap BasicDNS*) a **Custom DNS** (DNS Personalizado).
6. Pega los 4 servidores de nombres de AWS en las líneas correspondientes:
   * *Línea 1*: `ns-1025.awsdns-00.org`
   * *Línea 2*: `ns-154.awsdns-19.com`
   * *Línea 3*: `ns-782.awsdns-33.net`
   * *Línea 4*: `ns-1981.awsdns-56.co.uk`
   *(Nota: Asegúrate de eliminar cualquier punto final `.` si se copia de la consola de AWS, aunque Namecheap generalmente los remueve solos).*
7. Haz clic en el **icono de la marca de verificación verde (Save/Guardar)** a la derecha de los campos para guardar los cambios.

### Verificación de Propagación DNS
El cambio de servidores DNS no es instantáneo. Suele tardar de **5 minutos a 2 horas** (máximo 24-48 horas en casos raros).
* Puedes consultar si la propagación ya ocurrió ejecutando en tu terminal:
  ```bash
  dig cleanmybelly.com NS
  ```
  O usando herramientas web gratuitas como [DNSChecker.org](https://dnschecker.org/) buscando registros **NS**.

---

## Paso 4: Crear y Validar los Certificados SSL (ACM)

Una vez que el dominio ya apunta a los Name Servers de AWS, puedes proceder a solicitar y validar los certificados SSL de tus entornos.

1. Ve a la carpeta de certificados:
   ```bash
   cd ../certificates
   ```
2. Inicializa Terraform y ejecuta el despliegue:
   ```bash
   terraform init
   terraform apply
   ```

Este proceso:
1. Consultará tu zona DNS mediante AWS API (usando un bloque `data`).
2. Creará las solicitudes de certificados SSL en ACM.
3. Creará automáticamente los registros de validación CNAME dentro de tu zona hospedada en Route 53.
4. Esperará la validación. Como los Name Servers ya están apuntando a AWS, **la validación de ACM se completará con éxito en 2 a 5 minutos** sin quedarse colgada.
