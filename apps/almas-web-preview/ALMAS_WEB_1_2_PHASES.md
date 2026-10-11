# ALMAS Web 1.2 — cinco fases, firewall productivo y gates

Las cinco fases se implementan como **componentes aislados**, no como una
migración del motor ALMAS. La revisión de esta rama no implica publicación
ni habilitación de análisis privados.

| Fase | Componente | Contrato de aceptación |
|---|---|---|
| 1. JSON Schema Draft 2020-12 completo | `build_schema_registry.py`, `browser-schema-entry.mjs` | empaquetar la clausura transitiva de esquemas canónico/M30/M31, resolver $ref sin llamadas de red, validar canonical, M30 y M31, rechazar datos inválidos; no mostrar datos antes de validar |
| 2. Grafo documental M17 | `evidence-graph.mjs` | nodos y enlaces solo desde IDs y familias declaradas, tope de nodos, sin inferir independencia de contactos |
| 3. Vista astrológica | `astrology-view.mjs` | mostrar posiciones, longitudes, casa, signo, regente, decanato y retrogradación **solo cuando figuren** en canonical; indicar ausencias de carta compuesta, Davison, védica, dracónica y otras modalidades |
| 4. Modelo declarativo M30/M31 | `report-view.mjs` | importar outputs oficiales en el navegador, validar tres schemas, estados compatibles y SHA-256 canónico; exportar HTML local solo con todos los gates cumplidos; 12 secciones, no fabricar narrativa |
| 5. Privacidad y preparación | `private_gate.py`, `PRIVATE_DATA_GO_NO_GO.md` | denegar toda solicitud personal hasta auth/consentimiento/auditoría formal; APIs remotas existentes **solo sintéticas** |

## Compilación y pruebas

Desde el checkout del repositorio:

```bash
cd apps/almas-web-preview
npm install --no-audit --no-fund
npm run build
cd ../..
node --test apps/almas-web-preview/test/*.test.mjs
PYTHONPATH=src:tests python -m unittest discover -s apps/almas-api-sandbox -p 'test_*.py' -v
```

El validador AJV se empaqueta en `full-schema-validator.mjs` con un registro
generado desde la **clausura transitiva** de referencias JSON Schema oficiales requeridas por canonical/M30/M31, sin resolver URLs
externas. El fichero compilado se genera en el build; **no** se debe
desplegar un `app.mjs` que lo invoque sin incluirlo. Si faltan
esquemas, la importación falla cerrada.

## Limitaciones explícitas

- El navegador solo muestra cartas según la geometría **disponible**.
  No se prometen efemérides, posiciones védicas, antiscios, decanatos ni
  cartas compuestas no declaradas. Para generarlas, ALMAS debe aportar
  salidas canónicas con esquemas y procedencia verificable.
- La huella M30 usa la serialización Python del objeto canónico. El
  navegador compara SHA-256 de una serialización con claves ordenadas;
  si existen diferencias de formato numérico, **bloquea** la
  exportación en vez de acreditar una falsa coincidencia.
- La exportación es del **modelo documental declarativo**, a HTML
  imprimible. La generación de informes narrativos oficiales, PDF/DOCX
  profesional y sus preflight permanecen en el pipeline de publicación,
  no en este visor.
- Vercel Authentication protege Preview, pero no autentica a sujetos
  individuales. No se incorpora una API para analizar datos privados.
- Las fases 1-4 no cambian `src/almas_tfa`, `schemas/`, los índices
  IEM/IDD/IRC/IAT/ICC/ICE, pesos, scoring, ontología ni Atacires
  SHADOW/NO-GO. La fase 5 conserva el NO-GO productivo.

## Plan de revisión

1. CI: compilación AJV completa y pruebas contra fixture canónico
   positivo/negativo, graph, chart, integrity y límites.
2. Revisión del diff limitada a las dos aplicaciones y al workflow.
3. Preview Vercel aislada con assets completos y Vercel Authentication.
4. HTTPS 200 de recursos estáticos y no regresión de los dos endpoints
   sintéticos. Nunca publicar URL de bypass ni secretos.
5. Merge condicionado a todos los workflows del HEAD en PASS; cualquier
   cambio de motor productivo requiere PR y review independiente.

**Definición de completado**: las fases de visualización y consulta quedan
implementadas y probadas; la fase 5 se considera cerrada como arquitectura
NO-GO y política de seguridad, no como producto privado habilitado.
