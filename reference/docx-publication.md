# Publicación DOCX · ALMAS B5

## Posición en el pipeline

La publicación DOCX comienza después de que el contenido interpretativo esté cerrado:

`canonical_analysis → M30 → M31 → authored_report → DOCX → PDF/preflight`

Para el perfil personal:

`personal_canonical_analysis → personal_report_document_model → personal_authored_report → DOCX → PDF/preflight`.

El DOCX no es una nueva capa analítica ni hermenéutica. Materializa el texto ya aprobado en la superficie de autoría correspondiente.

## Perfiles B5

La infraestructura es compartida. El perfil relacional conserva `ALMAS_B5_BOOK_V1`; el adaptador personal usa `ALMAS_B5_PERSONAL_BOOK_V1` con la misma geometría y estilos base.

### Geometría común

El primer perfil editorial se orienta a informes largos y lectura tipo libro:

- formato: ISO B5 vertical;
- tamaño: 176 × 250 mm;
- márgenes: 18 mm;
- cuerpo: 10,5 pt;
- títulos de sección: 16 pt;
- portada y contenido inicial;
- cada sección canónica comienza en página nueva;
- bibliografía al final;
- pie con huella canónica abreviada y número de página.

No se embeben fuentes tipográficas. El generador declara familias de uso común y permite sustitución por el procesador de textos.

## Fidelidad del contenido

`build_authored_report_docx()` y `build_personal_authored_report_docx()` no resumen, reescriben ni recalculan. `build_report_docx()` selecciona el adaptador por `document_kind`.

Para cada sección `AUTHORED`:

1. copia literalmente `narrative`;
2. conserva el título;
3. representa los límites interpretativos;
4. añade una nota secundaria de trazabilidad con evidencias, claims y fuentes cuando existen.

La nota de trazabilidad queda visualmente subordinada para que el aparato metodológico no eclipse la lectura.

Una sección `OMITTED_NOT_AVAILABLE` se representa como no disponible; no se rellena imaginativamente.

## Bibliografía

La bibliografía procede exclusivamente de `authored_report.bibliography`.

El DOCX puede mostrar etiqueta, localizador y URL, pero esa materialización no modifica pesos, modelos ni estados analíticos.

## Dependencia

La implementación utiliza el extra opcional:

`publication-docx = ["python-docx==1.2.0"]`

La dependencia no forma parte del núcleo analítico.

## Verificación

El workflow `Publicación DOCX` está limitado por rutas y ejecuta:

- generación en Python 3.10 y 3.12;
- apertura posterior del DOCX;
- comprobación de B5;
- presencia literal de todas las narrativas exigidas por la superficie; el perfil relacional conserva once secciones y el personal respeta el orden de su `report_profile`;
- bibliografía;
- fingerprint;
- inmutabilidad del `authored_report`.

La inspección visual completa se realiza fuera del workflow mediante render DOCX → páginas antes de declarar cerrado el perfil material.

## Límite de este bloque

Este paso termina en DOCX.

Conversión PDF, preflight, sangrados, requisitos de imprenta y verificación final pertenecen al bloque siguiente.
