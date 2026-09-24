# ALMAS · Arquitectura de dos skills

ALMAS utiliza dos motores metafísicos especializados que se entrelazan sin confundirse.

## Skill A · Astrología Metafísica Relacional

Entrada principal: datos astronómicos/natales y eventos.

Función: observar e inferir metafísicamente la arquitectura del alma y del vínculo mediante astrología.

Produce:

- geometría natal y relacional;
- raíces independientes;
- pilares;
- modelos AF/KA/AG/LG;
- ejes ontológicos;
- temporalidad;
- robustez;
- cobertura;
- contraevidencia.

Salida canónica principal: `canonical_analysis.json`.

Salida de interoperabilidad: `astrology_to_soul_contract.json`.

## Skill B · Contrato Álmico

Entrada principal: `astrology_to_soul_contract.json`.

Puede añadir doctrina, historia, cronología, hechos y otros módulos metafísicos documentados.

Función: reconstruir la posible arquitectura preencarnatoria:

- motivo del encuentro;
- funciones A_EN_B y B_EN_A;
- campo común;
- cláusulas;
- roles;
- karma/dharma;
- aprendizaje;
- reparación;
- misión;
- integración;
- transformación;
- cierre.

Salida: `canonical_soul_contract.json`.

## Relación entre motores

```text
DATOS
  ↓
ASTROLOGÍA METAFÍSICA
  ↓
canonical_analysis.json
  ↓
astrology_to_soul_contract.json
  ↓
CONTRATO ÁLMICO
  ↓
canonical_soul_contract.json
  ↓
INFORME HERMENÉUTICO
```

La segunda skill no vuelve a contar como nuevas confirmaciones las mismas técnicas ya consolidadas por la primera.

## Principio metafísico

La separación es funcional, no filosófica. Ambos motores trabajan dentro del paradigma metafísico ALMAS.

La astrología no es un apéndice decorativo del análisis: es un instrumento principal de averiguación metafísica.

Los controles de robustez, dependencia y contraevidencia son mecanismos de rigor interno.

## Versionado independiente

- paquete/motor astrológico raíz: SemVer propio;
- `ALMAS Soul Contract`: SemVer propio;
- bridge astrology→contract: versión de contrato propia.

Un cambio doctrinal en Soul Contract no obliga a modificar el motor astrológico. Un cambio de cálculo astrológico sólo exige nueva versión del bridge si rompe su contrato de datos.
