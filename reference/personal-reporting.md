# Informes astrológicos personales · contrato 1.21

## Posición arquitectónica

El perfil personal es una superficie interna de la única skill ALMAS. No añade una segunda versión pública ni modifica M00–M31.

Las dos primeras fases 1.21 cubren:

`natal normalizado → personal_canonical_analysis → validación/fingerprint → personal_report_document_model → personal_authored_report`.

La adaptación DOCX/PDF y el preflight se incorporarán en el bloque posterior.

## Minimización de datos

`personal_canonical_analysis` no requiere fecha, hora, lugar ni coordenadas brutas. Conserva un `subject_id`, la calidad de hora y la carta natal normalizada. La geometría procede de `natal-chart.schema.json`.

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

El modelo documental declara `reuse_existing_publication_infrastructure=true` y `adapter_status=PENDING_ADAPTER`.

Esto es deliberado: 1.21 no duplica el renderer B5 de 1.20. La siguiente fase deberá adaptar la infraestructura existente a secciones P01–P11 sin romper el perfil relacional S01–S11.

## Invariantes

- no almacenar datos brutos personales si el canonical no los necesita;
- no inventar hora, lugar o coordenadas;
- no aceptar carta natal personal sin provenance del backend;
- no permitir network I/O ni geocodificación implícita en provenance de producción;
- no confundir calidad de cálculo con calidad de hora natal;
- no permitir que el perfil de informe cambie la interpretación analítica;
- no crear scores relacionales, discriminadores u ontología por introducir un informe personal.
