# Router de fuentes para informes personales · ALMAS 1.21

## Función

El router convierte los dominios calculados por `route_personal_reference_domains()` en referencias concretas ya existentes en `reference/source-registry.json`.

No crea fuentes, no asigna pesos y no transforma presencia bibliográfica en evidencia estructural.

## Estados

`SUPPORTED` indica que el corpus actual contiene fuentes adecuadas para la función declarada.

`PARTIAL` indica que existen fuentes útiles, pero el dominio conserva una carencia relevante. Dos casos se mantienen deliberadamente parciales:

- `evolutionary`: el corpus contiene astrología orientada al crecimiento, pero no una fuente metodológica registrada de la escuela formal de Astrología Evolutiva;
- `kabbalah`: el corpus contiene doctrina primaria y análisis académico sobre alma, gilgul, raíz y zivug, pero eso no equivale a un método natal de astrología cabalística.

`SOURCE_GAP` significa que el router no dispone todavía de una fuente registrada adecuada. `fixed_stars` permanece en este estado; no se completa con una referencia ad hoc.

## Clases epistemológicas

Cada dominio declara `epistemic_scope`. Una misma ruta puede contener técnica y doctrina, pero la autoría posterior debe mantenerlas separadas.

La categoría `karmic`, por ejemplo, puede enrutar tanto un método astrológico identificado como una fuente doctrinal reencarnacionista. La coexistencia bibliográfica no convierte ambas fuentes en una misma clase de evidencia.

## Resolución

`route_personal_reference_sources(canonical, source_registry)`:

1. obtiene los dominios requeridos por el canonical;
2. carga `ALMAS_PERSONAL_REFERENCE_ROUTER_V1`;
3. verifica que todo `source_id` exista en el registro canónico;
4. devuelve los dominios, estados, fuentes e internal refs;
5. expone `source_gaps` sin rellenarlos.

`enrich_personal_canonical_sources()` devuelve una copia del canonical y añade a `source_trace` únicamente fuentes ya registradas. No modifica el cálculo natal ni añade doctrina al canonical.

## Fuente única

El manifiesto vive en `src/almas_tfa/data/personal-report-reference-router.json` para estar disponible en instalaciones del paquete. No duplica la metadata bibliográfica. Autor, obra, prioridad, tradición y verificación siguen procediendo exclusivamente de `reference/source-registry.json`.

## Invariantes

- ningún `source_id` inexistente puede resolverse;
- un gap permanece explícito;
- presencia de una fuente no incrementa scores;
- doctrina y técnica no se fusionan;
- el enriquecimiento no muta el canonical de entrada;
- las referencias internas de publicación no se presentan como fuentes doctrinales.
