---
name: almas-personal-astrology-report
description: Punto de entrada especializado interno de ALMAS 1.11.0 para construir informes astrológicos personales trazables y publicables en PDF a partir de un análisis canónico individual. No constituye una segunda skill pública.
version: 1.11.0
kind: internal_module
independent_versioning: false
engine_revision: 1.0.0
author: Proyecto ALMAS
---

# ALMAS · Módulo de Informes Astrológicos Personales PDF

## 0. Naturaleza del módulo

Este directorio es un punto de entrada especializado dentro de la única skill pública ALMAS. Hereda `VERSION=1.11.0` y no mantiene SemVer independiente.

Su objetivo es producir informes personales completos sin convertir el PDF, la narrativa o la maquetación en una fuente analítica. La única verdad del informe es `personal_canonical_analysis.json`.

## 1. Principio de separación

Flujo obligatorio:

`datos de nacimiento/documentos → cálculo → personal_canonical_analysis.json → validación/fingerprint → personal_report_document_model.json → narrativa → DOCX → PDF → preflight → render completo → inspección → corrección → verificación`

La fase de interpretación nunca recalcula silenciosamente posiciones, casas, aspectos u otras geometrías.

## 2. Capas epistemológicas

Toda afirmación material conserva:
- `A_CALCULATED`: dato astronómico, geométrico o documental;
- `B_TECHNIQUE`: técnica empleada;
- `C_DOCTRINE`: doctrina explícita atribuible a una fuente;
- `D_CONTEMPORARY_USAGE`: uso contemporáneo documentado;
- `E_PROJECT_HYPOTHESIS`: síntesis interpretativa de ALMAS.

Nunca presentar E como C.

## 3. Datos mínimos

No inventar fecha, hora, huso, lugar ni coordenadas.

Registrar:
- fecha local;
- hora local;
- zona IANA cuando exista;
- lugar y coordenadas;
- calidad de hora natal A/B/C/D;
- fuente de la hora;
- sistema zodiacal;
- sistema de casas;
- nodo verdadero/medio;
- backend y versión;
- ephemeris path/fuente;
- flags u opciones de cálculo;
- hash de entrada cuando sea posible.

Si la hora es C o D, degradar casas, ángulos y técnicas sensibles a la hora.

## 4. Jerarquía analítica personal

Orden base:
1. radix, ASC–DSC, MC–IC, luminarias y regente del ASC;
2. elementos, modalidades, hemisferios, dignidades, secta, regencias y dispositores;
3. aspectos mayores y configuraciones dominantes;
4. casas, cúspides y proximidad a cúspides;
5. nodos y Quirón;
6. declinaciones;
7. antiscios y contra-antiscios;
8. puntos medios;
9. lotes/partes con fórmula declarada;
10. dracónica individual como capa moderna/esotérica;
11. estrellas fijas y parans;
12. asteroides como refinamiento subordinado;
13. temporalidad.

Ninguna capa secundaria puede invertir por sí sola una conclusión estructural sólida.

## 5. Escuelas interpretativas

Distinguir explícitamente:
- tradicional/clásica;
- moderna/psicológica;
- humanista;
- evolutiva;
- kármica;
- dracónica;
- esotérica;
- cabalística comparada.

No fusionar escuelas. Cuando una escuela no contiene una técnica o concepto, no retroproyectarlo.

## 6. Temporalidad

Puede incluir:
- tránsitos;
- progresiones secundarias;
- arco solar;
- profecciones;
- revoluciones solares;
- retornos planetarios;
- eclipses;
- ciclos sinódicos;
- atacires/direcciones.

Las técnicas temporales describen activación de una estructura natal. No garantizan acontecimientos.

Una carta de retorno con casas exige localidad real documentada para el momento del retorno. Si no existe, usar representación zodiacal sin casas/ángulos.

## 7. Capa esotérica y cabalística

Usar conceptos de alma, propósito, rayos, tikkun, tzimtzum, shevirat, nitzotzot, birur, sefirot u otros únicamente como lectura simbólica/doctrinal.

Mantener separadas:
- Kabbalah judía histórica;
- Qabalah hermética;
- astrología esotérica moderna;
- hipótesis comparativas de ALMAS.

No usar una correspondencia moderna para afirmar que un texto histórico enseña astrología que no contiene.

## 8. Contraevidencia

Todo informe completo busca:
- configuraciones que contradigan la síntesis preferida;
- dependencia excesiva de una sola técnica;
- inestabilidad por hora natal;
- idealización interpretativa sin soporte estructural;
- conflicto entre escuelas;
- datos documentales ausentes o inconsistentes.

La intensidad de una lectura no aumenta su nivel de evidencia.

## 9. Perfiles de informe

Perfiles admitidos:
- `EXECUTIVE_PERSONAL_REPORT`;
- `STANDARD_PERSONAL_REPORT`;
- `FULL_CRITICAL_REPORT`;
- `TECHNICAL_ATLAS`;
- `ESOTERIC_KABBALISTIC_REPORT`.

El perfil selecciona secciones y profundidad; nunca modifica el análisis canónico.

## 10. Diseño editorial B5

Perfil editorial de referencia para informes extensos:
- B5 vertical 176 × 250 mm;
- cuerpo serif Unicode alrededor de 10.5 pt;
- sans serif para títulos y navegación;
- margen interior suficiente para encuadernación;
- portadillas en recto;
- blancos editoriales mudos;
- cabeceras enfrentadas;
- pies de figura coherentes;
- tablas legibles, normalmente no inferiores a 8–8.5 pt;
- figuras preferentemente ≥ 270 ppp efectivos;
- índices y marcadores PDF cuando proceda.

El formato puede cambiar si el usuario o la imprenta especifican otro objetivo.

## 11. QA de publicación

No considerar final un PDF hasta verificar:
- tamaño de página;
- fuentes embebidas;
- ausencia de Type 3/emoji cuando exista alternativa vectorial;
- resolución de imágenes;
- tablas partidas;
- glifos rotos;
- viudas/huérfanas manifiestas;
- blancos y portadillas;
- numeración;
- índice y marcadores;
- ausencia de clipping/overlap;
- render visual del 100 % de las páginas;
- preflight final.

No declarar PDF/X, CMYK/ICC o conformidad de imprenta salvo conversión y comprobación específicas.

## 12. Enrutamiento de referencias

Cargar solo los módulos doctrinales/técnicos necesarios para el caso. El router canónico está en `manifests/personal-report-reference-router.json`.

La recuperación modular evita usar todo el corpus indistintamente y mantiene trazabilidad de qué escuela sustenta cada lectura.

## 13. Contratos

Entrada:
- `schemas/personal-report-request.schema.json`.

Verdad analítica:
- `schemas/personal-canonical-analysis.schema.json`.

Modelo documental:
- `schemas/personal-report-document-model.schema.json`.

Código:
- `src/almas_tfa/personal_report_handlers.py`.

## 14. Invariantes

- No inventar datos natales.
- No generar casas de retorno sin localidad real.
- No convertir una técnica secundaria en eje estructural único.
- No confundir doctrina con hipótesis.
- No inferir diagnóstico médico, salud mental, delitos, fidelidad o decisiones futuras desde astrología.
- No permitir que la narrativa cambie valores canónicos.
- No permitir que el perfil de informe cambie la conclusión analítica.
- No publicar datos privados como fixtures del repositorio.
