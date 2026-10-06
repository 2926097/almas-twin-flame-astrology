# ALMAS · Uso del núcleo temporal Atacires

El recorrido relacional admite `request.atacires_requests`, una lista de objetos con `subject_id` y `settings`. `prepare_relational_raw_input` la conserva y `configured_handlers` registra el decorador M26 tanto con backend astronómico como sin él. La ejecución exige que M02 ya haya producido la carta canónica correspondiente, con instante, coordenadas y provenance coherentes con el sujeto. No se obtiene otra carta desde Swiss ni se envían datos a un servicio externo.

```json
{
  "atacires_requests": [{
    "subject_id": "A",
    "settings": {
      "start_utc": "2026-01-01T00:00:00Z",
      "end_utc": "2027-01-01T00:00:00Z",
      "cycle_years": 60,
      "year_days": 365.2422,
      "direction": "direct",
      "promissors": ["SUN"],
      "significators": ["MOON"],
      "aspects_deg": [0, 90, 180],
      "orb_deg": 1,
      "output_timezone": "Europe/Madrid"
    }
  }]
}
```

El fragmento se añade al raw_input o dentro de `request` en la envolvente relacional existente; no es por sí solo una solicitud completa. La variable `ALMAS_TEMPORAL_ATACIRES_ENABLED=true` habilita el cálculo. Su ausencia o `false` preserva el comportamiento anterior. El bloque consultable en el análisis canónico es `temporal.atacires_shadow`: `status`, `signals`, `calculations` y `diagnostics`. `scoring_enabled` siempre es false. Un error en cualquiera de las solicitudes invalida atómicamente el lote, conserva vacías sus señales y registra NOT_EVALUABLE.

La API Python interna recibe `build_uniform_cycle_request(chart, subject, settings)` y devuelve `calculate_uniform_cycle(request)`. La hora no documentada o con incertidumbre se rechaza para ese cálculo exacto; para estudiarla se aportan cartas recalculadas con la infraestructura de robustez vigente y se comparan sus resultados mediante `assess_robustness`. El índice IAT productivo y cualquier clasificación de origen siguen perteneciendo a ALMAS.
