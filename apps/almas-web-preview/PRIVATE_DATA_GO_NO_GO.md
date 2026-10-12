# ALMAS 1.2 — barrera de privacidad, fase 5

Estado: **NO-GO para análisis remotos de personas reales**.

Esta fase prepara un contrato de seguridad, no autoriza el tratamiento
de datos privados. La aplicación conserva la lectura de JSON en memoria
local y sus dos peticiones GET existentes, exclusivamente sintéticas.

## Requisitos de autorización productiva

- Identidad personal mediante proveedor OIDC mantenido, MFA y sesiones rotatorias
- Autorización por caso y prueba de aislamiento entre identidades e inquilinos
- Base jurídica, finalidad, información a sujetos, gestión de consentimiento
  cuando resulte aplicable y procedimiento de revocación
- Minimización de datos natales e identificadores; cifrado TLS y en reposo
- Políticas de retención/borrado, respaldos y gestión de claves
- CSRF y controles de subida, límites de tamaño/frecuencia, SSRF y rate limiting
- Prohibición de datos privados en logs, analytics, trazas, URL y CI
- Revisión de seguridad y privacidad, tests de aislamiento y pentest
- Validación oficial M30/M31, procedencia astronómica y validación de fuentes
- Autorización humana expresa antes de cualquier nueva ruta de datos personales

## Controles existentes

La importación de `canonical_analysis.json` permanece en el navegador.
Los endpoints GET en Vercel y Render solo procesan archivos sintéticos.
El nuevo módulo `private_gate.py` deniega toda autorización de procesos privados,
y no forma parte de ningún endpoint.

No se activarán cuentas, datos personales ni producción en este programa.
Atacires permanece SHADOW/NO-GO; índices, esquemas y ontología inalterados.

## Búsqueda de ciudad de nacimiento (Preview Web 1.3)

El formulario contiene un buscador de localidades independiente del procesamiento natal. Solo cuando el usuario pulsa **Buscar ciudad** se envía el nombre textual tecleado mediante GET directo a `geocoding-api.open-meteo.com` con parámetros fijos `count=10,language=es,format=json`; se omiten credenciales y referer. Open-Meteo puede observar la consulta y metadatos técnicos de conexión (véase su política de privacidad). No se envían a ese proveedor nombre de personas, fecha/hora de nacimiento, perfil relacional ni documento canónico.

El usuario selecciona manualmente una localidad y entonces se rellenan en el navegador zona IANA y coordenadas WGS84 ocultas. Ninguna de ellas se remite a Vercel ni a Render para un cálculo privado. El servidor Python permite esta única salida de geocodificación en su CSP, pero continúa escuchando solo en loopback. Búsqueda no autorizada, incompleta o fallida bloquea el envío al motor. La precisión de localidad y zona horaria histórica se verifican por separado; **no cambia el NO-GO de los análisis privados remotos**. El servicio gratuito externo está sujeto a condiciones no comerciales y atribución CC BY 4.0.
