# ALMAS — publicación editorial local de 12 secciones (fase experimental)

La versión M31 del visor Web tiene 12 secciones (S01–S12), mientras que el
`authored-report.schema.json` productivo y el exportador B5 relacional siguen
exigiendo 11 secciones. **Este módulo no modifica ni sustituye esos contratos.**
Define un formato LOCAL EDITORIAL independiente, `ALMAS_LOCAL_EDITORIAL_12_V1`,
para permitir redacción manual respaldada por rutas canónicas y exportación B5.

## Entrada directa desde el motor integral local

Tras calcular M00–M31 en `http://127.0.0.1`, usar **Exportar resultados locales**
para descargar `almas-local-results.json`. Esta exportación se genera solamente
después de una acción explícita del usuario; no debe subirse a GitHub, Vercel,
Render ni a ninguna herramienta de diagnóstico remota. Contiene datos
potencialmente personales y permanece bajo control del usuario.

Ahora el comando admite `--bundle`, que extrae en memoria los tres documentos
del fichero local sin escribir copias intermedias ni modificar el motor:

```bash
PYTHONPATH=src python apps/almas-web-preview/local_editorial_12.py \
  --bundle /CARPETA/PRIVADA/almas-local-results.json \
  --scaffold-out /CARPETA/PRIVADA/borrador-12.json

# Tras redactar y contrastar todas las secciones disponibles:
PYTHONPATH=src python apps/almas-web-preview/local_editorial_12.py \
  --bundle /CARPETA/PRIVADA/almas-local-results.json \
  --authored /CARPETA/PRIVADA/borrador-12.json \
  --docx-out /CARPETA/PRIVADA/almas-informe-12.docx \
  --pdf-out /CARPETA/PRIVADA/almas-informe-12.pdf
```

El modo original de tres archivos sigue vigente. Ambos modos pasan
exactamente por la misma validación de schemas oficiales, huellas M30/M31,
estado de reportabilidad, 12 secciones, trazabilidad epistemológica y
preflight PDF B5. Se rechazan claves JSON duplicadas (también anidadas),
valores numéricos JSON no finitos, documentos ausentes y estados divergentes.
El paquete no redacta automáticamente ni confirma hipótesis metafísicas.
Se preserva el contrato productivo de **11 secciones**.

## Flujo offline

A partir de una ejecución real M00–M31 con `canonical_analysis.json`,
`report_gate.json` (M30) y `report_document_model.json` (M31), crea primero
el borrador:

```bash
PYTHONPATH=src python apps/almas-web-preview/local_editorial_12.py \
  canonical_analysis.json report_gate.json report_document_model.json \
  --scaffold-out /CARPETA/PRIVADA/borrador-12.json
```

Cada sección aparece vacía. Añade una narrativa editada y revisada, las rutas
de `available_paths` en el modelo M31, clases epistemológicas permitidas,
fuentes existentes en `bibliography` cuando se utilice doctrina o prácticas
contemporáneas, y limitaciones. **Nunca asignar puntuaciones a estados nulos,
inventar casas/posiciones ni convertir hipótesis espirituales en hechos.**

Después de completar las 12 secciones disponibles:

```bash
PYTHONPATH=src python apps/almas-web-preview/local_editorial_12.py \
  canonical_analysis.json report_gate.json report_document_model.json \
  --authored /CARPETA/PRIVADA/borrador-12.json \
  --docx-out /CARPETA/PRIVADA/almas-informe-12.docx \
  --pdf-out /CARPETA/PRIVADA/almas-informe-12.pdf
```

Requiere `python-docx==1.2.0`, `pypdf==6.19.0` y LibreOffice
`soffice` **en el equipo local**, más `jsonschema` y las dependencias
normales ALMAS. El PDF pasa el preflight B5 (tamaño, cropbox, fuentes
incrustadas, páginas vacías, texto completo y ausencia de cifrado).
El contrato bloquea M30/M31 divergentes, 12 secciones desordenadas, valores
no trazables, doctrina sin fuente, secciones ausentes redactadas o ausencia
de narrativa en secciones disponibles.

No hay IA redactora conectada ni prompts externos; el fichero de borrador
queda siempre privado. Si la narrativa no está completa y trazada, no se
publica nada. El formato nuevo es **experimental, no reemplaza al contrato
oficial** `ALMAS_AUTHORED_REPORT` de 11 secciones. Para promocionarlo
será necesaria una migración versionada del schema, auditoría semántica
y regresiones de publicación, sin alterar puntuaciones ni ontología.

Pruebas en GitHub Actions: `ALMAS Web · publicación editorial local 12 secciones`
genera un PDF con texto exclusivamente sintético. No sube informes ni
documentos privados.
