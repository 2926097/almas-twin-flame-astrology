# Auditoría final de release · ALMAS 1.11.0

**Fecha:** 25 de septiembre de 2026  
**Rama auditada:** `audit/arquitectura-2026-09-25`  
**Base:** `main`  
**Tipo de release:** MINOR compatible hacia atrás  
**Estado documental:** preparado para validación final de CI; no fusionado a `main`.

## 1. Objeto

Esta auditoría cierra la transición de ALMAS desde una arquitectura principalmente normativa hacia una **única skill pública modular con pipeline ejecutable M00–M31**, preservando las reglas metodológicas y ontológicas ya congeladas.

La release 1.11.0 añade capacidad ejecutable y contratos de integración. No redefine la metafísica del proyecto ni modifica silenciosamente criterios para ajustarlos a un caso concreto.

## 2. Arquitectura pública

Se mantiene una sola skill pública:

`almas-twin-flame-astrology`

El módulo de Contrato Preencarnatorio permanece como módulo interno especializado y hereda el SemVer de la raíz. Su `engine_revision` histórica sigue separada del versionado público.

Flujo principal:

`raw_input → M00…M31 → canonical_analysis.json → report_gate → report_document_model.json`

La reconstrucción preencarnatoria consume evidencia canónica; no debe recalcular silenciosamente la astrología.

## 3. Ejecución M00–M31

La release incorpora:

- contrato común de ejecución modular;
- orquestador secuencial;
- registro de implementación por módulo;
- propiedad explícita de namespaces canónicos;
- ejecución sintética FULL de las 32 etapas;
- M01 y M03–M31 con handlers ejecutables;
- fronteras de backend inyectables para M02 natal y M08 Davison;
- geometría relacional, simetrías, dracónicas, lotes y capa simbólica secundaria;
- grafo de evidencia, deduplicación y raíces independientes;
- scoring estructural, contraevidencia y discriminación;
- ablación, sensibilidad horaria, modelos nulos y robustez;
- activación temporal anclada y eventos documentales;
- doctrina/hermenéutica con firewalls A–E;
- viabilidad y reciprocidad factual;
- gate M30;
- modelo documental M31.

M31 cierra el **pipeline analítico**. No renderiza DOCX ni PDF y no debe modificar la verdad canónica.

## 4. Invariantes preservados

Esta release no cambia:

- fórmulas IEM, IDD, IRC, IAT, ICC o ICE;
- pesos estructurales;
- thresholds del gate `SUPPORTED`;
- pilares AF/KA/AG/LG;
- reglas de independencia;
- firewall de contraevidencia;
- ontología multiaxial;
- discriminadores ontológicos;
- regla de que rareza estadística no es probabilidad metafísica;
- regla de que temporalidad activa arquitectura previa pero no la crea;
- regla de que capas `support_only` no crean ontología;
- separación A_CALCULATED / B_TECHNIQUE / C_DOCTRINE / D_CONTEMPORARY_USAGE / E_PROJECT_HYPOTHESIS.

## 5. Contrato canónico e informe

`canonical_analysis.json` continúa siendo la única verdad analítica.

M30:

- distingue `READY`, `PARTIAL` y `BLOCKED`;
- calcula fingerprint canónico;
- bloquea divergencias entre entrada bruta y snapshot.

M31:

- produce `report_document_model.json`;
- organiza 11 secciones canónicas;
- conserva referencias a rutas de datos;
- no incrusta valores alterados;
- no redacta conclusiones nuevas;
- no renderiza documentos.

## 6. Cobertura de tests

La suite Python de esta release contiene **133 tests deterministas**.

Incluye pruebas unitarias de módulos, firewalls metodológicos, contratos de schemas, orquestación y una ejecución sintética FULL M00–M31.

El validador público comprueba además:

- sincronía de versiones;
- archivos normativos;
- secuencia M00–M31;
- schemas y fixtures;
- fuentes, conceptos y genealogía;
- techos inferenciales;
- discriminadores;
- pipeline preencarnatorio;
- privacidad/publicación;
- convención lingüística de títulos de schemas.

## 7. Convención lingüística

La presentación humana activa del repositorio se normaliza al español.

Se conservan en inglés cuando son necesarios:

- identificadores de máquina;
- nombres de claves y enums;
- nombres históricos de archivos/rutas;
- títulos bibliográficos originales;
- citas o marcadores textuales directos;
- terminología original cuando forma parte del objeto histórico estudiado.

La traducción de prosa explicativa no altera IDs, referencias, orden de arrays usado por trazabilidad ni contratos de interoperabilidad.

## 8. Corpus y doctrina

Se mantienen las separaciones entre:

- antecedente histórico;
- doctrina explícita;
- descripción académica;
- uso contemporáneo;
- operacionalización ALMAS.

La genealogía doctrinal, el registro de fuentes, el corpus literario y el corpus luriano han sido normalizados lingüísticamente sin convertir analogías en equivalencias.

La doctrina nunca añade IEM por mera existencia.

## 9. Limitaciones conocidas

### Backend astronómico de producción

M02 y M08 tienen contratos ejecutables e inyección de backend, pero la selección/implantación del backend astronómico de producción permanece pendiente.

Esto no impide las pruebas sintéticas del pipeline, pero sí significa que 1.11.0 no debe presentarse como un motor efemérico autónomo completo desde datos natales crudos sin backend configurado.

### Validación externa

La infraestructura de preregistro está preparada, pero no se ha ejecutado todavía un holdout externo real preregistrado.

La coherencia interna y el paso de CI no constituyen validación científica de la astrología ni prueba empírica de ontologías metafísicas.

### Rendering documental

M31 genera el modelo documental analítico. La maquetación DOCX/PDF y su preflight pertenecen a una capa posterior de authoring/rendering.

## 10. Criterios de cierre de release

La rama puede considerarse **lista para merge** únicamente cuando:

1. `Núcleo Python` concluya `SUCCESS` sobre el HEAD final;
2. `Contrato público` concluya `SUCCESS` sobre el mismo HEAD;
3. la PR siga siendo fusionable;
4. no exista deriva de versión pública;
5. no se introduzca ningún cambio posterior en fórmulas, pesos, thresholds, ontología o discriminadores sin una auditoría metodológica separada.

## 11. Decisión de auditoría

ALMAS 1.11.0 representa una ampliación ejecutable sustancial y compatible hacia atrás de la arquitectura 1.10.1.

La release es apta para cierre técnico cuando satisfaga los criterios de CI anteriores. La fusión a `main` queda deliberadamente fuera de esta auditoría y requiere una acción posterior explícita.
