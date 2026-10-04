# Motor Jyotiṣa Relacional

La extensión es observacional y optativa. Procesa dos cartas, sus posiciones siderales, Chara Kārakas, D9, AL/UL/A7, Bindu, upagrahas y eventos. La salida no altera IEM, IDD, IRC, IAT, ICC, ICE ni la ontología. El plan depurado y sus decisiones de alcance están en [PLAN_1.26.0_DEPURADO.md](PLAN_1.26.0_DEPURADO.md).

## Ejecución

Instalar el extra opcional y ejecutar el ejemplo sintético:

```bash
python -m pip install -e '.[astronomy-vedic,schema-validation]'
almas-vedic pipeline examples/vedic-request.synthetic.json -o vedic-result.json
almas-vedic report examples/vedic-request.synthetic.json -o vedic-report.md
almas-vedic report-canonical vedic-result.json -o vedic-report.md
almas-vedic report-model vedic-result.json -o vedic-report-model.json
almas-vedic chart person.json
almas-vedic timing person.json --at 2026-10-08T12:00:00-04:00
almas-vedic sensitivity person.json
almas-vedic validate corpus.json
python scripts/validate_vedic_runtime.py
```

`person.json` contiene `birth` y, opcionalmente, `configuration`. `birth` exige `timestamp` ISO con offset, `latitude` y `longitude`. `timezone`, si aparece, es IANA y debe reproducir la hora y el offset; `birth_time_quality` declara la calidad documental. No se geocodifican nombres ni se rectifican horas automáticamente. Los comandos sinastría, eventos y pipeline usan el formato de dos sujetos del ejemplo. `events` procesa la misma envolvente que `pipeline`, conservando eventos y auditoría. `report` vuelve a ejecutar la petición bruta; `render_vedic_report(envelope)` redacta directamente desde una envolvente ya calculada sin recalcular astrología.

`chart_from_sidereal` permite usar posiciones precomputadas sin el extra astronómico, con procedencia explícita. Requiere los siete planetas clásicos, Rahu y Lagna en grados siderales. Ketu se deriva; si se proporciona, debe coincidir con el antípoda. El nodo medio/verdadero y el ayanāṃśa deben corresponder a las posiciones suministradas; la función no verifica por sí misma esa declaración.

## Integración

```python
from almas_tfa.vedic.pipeline import run_vedic_pipeline, attach_vedic, render_vedic_report

envelope = run_vedic_pipeline(request)
augmented = attach_vedic(canonical_analysis, envelope)
text = render_vedic_report(envelope)
```

`attach_vedic` copia el objeto, conserva sus campos y rechaza sobrescrituras. `schemas/canonical-analysis.schema.json` admite el bloque opcional y `schemas/vedic.schema.json` restringe sus estados. Esta extensión no recalibra el pipeline M00–M31 ni añade raíces a M17. La proyección textual propia permite revisar la capa VED; no se incorpora automáticamente a los informes DOCX/PDF anteriores ni al frontend.

Las fronteras de pipeline, attach y reporting requieren `schema-validation`, también para una envolvente desactivada. Rechazan estructuras incompletas, números no finitos, configuraciones incompatibles, hashes de cartas distintos, IDs duplicados, referencias inexistentes, recuentos incoherentes y períodos que no contienen el evento o no están anidados. Los orbes de sinastría y eventos rechazan booleanos. El validador comprueba integridad contractual; no recalcula ni certifica la astronomía declarada.

`report-canonical` y `report-model` aceptan la envolvente o un objeto con campo `vedic`; no necesitan efemérides para redactar. El modelo `ALMAS_VED_REPORT_V1` conserva todas las features, incluidas las no coincidentes, con su ruta al dato, endpoints, capas, signos, geometría, dependencia y límites de interpretación. Expone cobertura de entrada/salida y fingerprint canónico. D9 se presenta como coordenada divisional simbólica; Arudhas por signo no reciben una longitud física inventada. Casas, velocidades y otros campos ausentes permanecen explícitamente ausentes. Los eventos conservan fechas, intervalos de daśā, contactos y referencias estructurales. Similaridad, complementariedad y espejo son hipótesis E; no diagnostican identidad de alma ni reciprocidad.

## Auditoría metodológica de salida

Cada sinastría incluye `methodological_readiness`, que separa rasgos enumerados, coincidencias según la regla declarada y paquetes de dependencia. El número de paquetes no se presenta como número de observaciones independientes: `independent_root_count` permanece nulo y `statistical_independence_demonstrated` es falso hasta contar con una unidad estadística y una evaluación específica de dependencia. Aṣṭakūṭa conserva su desglose por componente y publica perfil, tablas, excepciones, orientación, componentes puntuados y bloqueos de verificación; la puntuación matrimonial total continúa nula mientras el perfil no esté documentado y probado.

IVED expone puertas explícitas de preregistro, calibración y validación externa, junto con los requisitos pendientes. `temporal_readiness` distingue `NOT_RUN` de una evaluación `DESCRIPTIVE_ONLY`, contabiliza eventos, resultados Vimśottarī y cartas de tránsito, y mantiene a cero las raíces temporales independientes. El informe debe decir expresamente cuándo no recibió eventos y, por tanto, no calculó activaciones. Una salida descriptiva nunca se redacta como predicción ni como puntuación de compatibilidad. Las condiciones de promoción y los límites de esta auditoría se detallan en [EVOLUCION_METODOLOGICA_R2.md](EVOLUCION_METODOLOGICA_R2.md).

## Procedencia y límites

Las fórmulas técnicas documentadas se contrastan con Rao (2000), capítulo 4 para upagrahas, 6.2.9 para D9, 8.2 para kārakas, 9.2 para Arudhas, 16.2–16.3 para Vimśottarī y 28.8 para Sahamas. Se declara el perfil de siete regentes de Arudha, sin implementar las reglas de fuerza de corregentes. Las combinaciones relacionales y cruces D1/D9 son hipótesis E de ALMAS. Los datos deity/shakti/tattva no se completan por memoria ni mediante atribuciones sin pasaje.

Las pruebas del backend comparan la conversión tropical→sideral con los flags siderales directos de Swiss. Es un contraste interno del mismo motor; no equivale a dos motores astronómicos independientes. Los ejemplos numéricos de Rao y el método elemental de D9 proporcionan referencias documentales separadas. No se declara `CROSS_VERIFIED` para toda la capa astronómica.

Aṣṭakūṭa completo permanece `NOT_EVALUABLE`, IVED escalar es nulo y la validación externa es `NOT_PERFORMED`. Prāṇapada, Yogatārās y los cruces con asteroides quedan aplazados por el alcance R1. Las relaciones por signo potencialmente conflictivas son datos para revisión; no prueban incompatibilidad factual ni contraevidencia ontológica. La ausencia de contactos requiere una hipótesis previamente especificada para tener valor contrario.

El backend usa Swiss/Moshier como extra comparativo de VED; el proveedor de producción MOIRA/JPL no cambia. Swiss Ephemeris tiene condiciones de licencia propias que deben respetarse en las distribuciones que incorporen su dependencia. No se redistribuyen textos ni código de terceros.

## Corpus y controles

`validate` recibe un objeto con `subjects`, cada uno con `id`, `birth` y `stratum`; `pairs` contiene pares de IDs. `stratum` es una etiqueta declarada por el investigador para preservar los criterios de cohorte relevantes; no se calcula a partir de creencias o etiquetas de relación. Las parejas observadas y autorrelaciones quedan excluidas de los controles. Una muestra con controles insuficientes lo declara y no crea pares artificiales para fingir completitud. Los sujetos reutilizados y la dependencia de observaciones se informan explícitamente.

Las ablaciones y Shapley miden cobertura de features y bundles; no incremento predictivo. La función Benjamini–Hochberg es una herramienta matemática con supuestos de dependencia; no produce automáticamente p-values ni valida el corpus. Para evaluación científica se requieren objetivos observables, diseño preregistrado, cohorte independiente, unidad estadística y contraste externo.
