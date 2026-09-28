# Informes astrológicos personales · contrato 1.21

## Posición arquitectónica

El perfil personal es una superficie interna de la única skill ALMAS. No añade una segunda versión pública ni modifica M00–M31.

La cadena personal 1.21 cubre:

`personal_report_request → backend astronómico vigente → personal_canonical_analysis → validación/fingerprint → personal_report_document_model → personal_authored_report → DOCX/PDF B5`.

La cuarta fase añade la construcción autónoma del canonical desde una solicitud natal, sin duplicar backend ni permitir opciones de cálculo que contradigan la configuración de producción.

## Solicitud y cálculo

`personal-report-request.schema.json` contiene los datos brutos necesarios para el cálculo y el `report_profile`. El backend se inyecta desde la infraestructura vigente; la solicitud no selecciona kernel, versión del provider, sistema de referencia ni política astronómica.

`build_personal_canonical_from_request()` usa `natal_request_from_subject()` y `AstrologyBackend.calculate_natal()`. La ruta pública exige la procedencia congelada de producción `ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1 / ALMAS_MOIRA_JPL_SPK_V1`.

Una imposibilidad de cálculo del backend permanece fail-closed y no se sustituye por datos inferidos.

## Minimización de datos

`personal_canonical_analysis` no persiste fecha, hora, lugar ni coordenadas brutas. Conserva un `subject_id`, la calidad de hora y una carta natal creada por lista blanca. El builder descarta `metadata` del backend —incluidos instante UTC, JD y coordenadas— porque podría permitir reconstruir los datos natales. La geometría procede de `natal-chart.schema.json`.

La procedencia astronómica se toma de `natal.backend_provenance`, conforme a `astronomy-backend-provenance.schema.json`. No existe un segundo contrato de backend para informes personales.

## Calidad de hora

Estados A/B permiten una lectura temporal/casas normal. C/D mantienen el canonical reportable pero lo degradan a `PARTIAL` mediante `TIME_SENSITIVE_FACTORS_REQUIRE_DOWNGRADE`.

La degradación no reescribe la carta: obliga a que la autoría posterior trate con cautela casas, ángulos y técnicas sensibles a la hora.

## Perfiles

Se conservan cinco perfiles internos:

- `EXECUTIVE_PERSONAL_REPORT`;
- `STANDARD_PERSONAL_REPORT`;
- `FULL_CRITICAL_REPORT`;
- `TECHNICAL_ATLAS`;
- `ESOTERIC_KABBALISTIC_REPORT`.

El perfil selecciona secciones P01–P11; nunca modifica el canonical.

## Dominios de referencia

El router parte de `foundations`, `traditional`, `modern_psychological` y `publication`, y añade sólo los dominios activados por el canonical: evolutionary, karmic, draconic, esoteric, kabbalah, lots, symmetry, fixed_stars, asteroids y timing.

El router selecciona corpus; no produce conclusiones.

## Publicación

El modelo documental declara `reuse_existing_publication_infrastructure=true` y `adapter_status=READY`.

El perfil personal utiliza `ALMAS_B5_PERSONAL_BOOK_V1` y `ALMAS_B5_PERSONAL_PDF_V1` sobre el mismo núcleo de estilos, geometría, conversión y preflight de 1.20. El perfil relacional S01–S11 conserva sus APIs y perfiles originales.

## Invariantes

- no almacenar datos brutos personales si el canonical no los necesita;
- no inventar hora, lugar o coordenadas;
- no aceptar carta natal personal sin provenance del backend;
- no permitir network I/O ni geocodificación implícita en provenance de producción;
- no confundir calidad de cálculo con calidad de hora natal;
- no permitir que el perfil de informe cambie la interpretación analítica;
- no crear scores relacionales, discriminadores u ontología por introducir un informe personal.
