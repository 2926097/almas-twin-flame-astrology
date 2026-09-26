# Política de aislamiento de casos privados · Paso 19

## Finalidad

El repositorio público ALMAS no es un almacén de expedientes personales.

La política canónica es:

`ALMAS_PUBLIC_DATA_ISOLATION_V1`.

Su finalidad es impedir que material privado, pseudonimizado o confidencial entre accidentalmente en ejemplos, fixtures, casos públicos, holdouts o documentación publicable.

## Clases publicables

Sólo se admiten como artefactos de caso:

- `SYNTHETIC`;
- `PUBLIC_VERIFIABLE`;
- `PUBLIC_METADATA_ONLY`.

Quedan prohibidas en el repositorio:

- `PRIVATE_CASE`;
- `PSEUDONYMIZED_PRIVATE`;
- `PRIVATE_HOLDOUT`;
- `CONFIDENTIAL`.

La pseudonimización no convierte un caso privado en público.

## Fixtures sintéticos

Todo JSON de `examples/` debe estar registrado en `examples/manifest.json` como `SYNTHETIC`.

Un fixture sintético debe declarar:

- `contains_real_person_data=false`;
- `contains_nonpublic_material=false`;
- `derived_from_private_case=false`;
- `reversible_from_private_case=false`.

No basta con cambiar nombres, fechas unos días, grados astrológicos o identificadores.

Un derivado reversible o una perturbación ligera de un caso privado continúa siendo material privado.

## Casos públicos

Todo JSON de `public_cases/` debe estar registrado en `public_cases/manifest.json` como `PUBLIC_VERIFIABLE`.

Cada caso exige:

- datos subyacentes ya públicos;
- `independently_verifiable=true`;
- `public_source_refs` no vacío;
- ausencia de material privado suplementario;
- separación de hechos públicos, cálculo e interpretación.

Una fuente pública no autoriza añadir comunicaciones privadas, datos natales no publicados o acontecimientos conocidos sólo por acceso personal.

## Holdouts

El repositorio reserva `validation/holdouts/` para:

- controles sintéticos;
- casos públicos verificables;
- metadatos públicos no identificables.

Un holdout privado puede existir fuera del repositorio.

El repositorio público sólo puede conservar sobre él:

- referencia externa opaca;
- referencia de preregistro;
- métricas agregadas no identificables.

No se publican entradas privadas, historias relacionales, mensajes, datos natales privados, resultados de caso individuales ni hashes reversibles de datos personales.

## Manifiestos exhaustivos

Los tres scopes públicos tienen manifiesto obligatorio:

- `examples/manifest.json`;
- `public_cases/manifest.json`;
- `validation/holdouts/manifest.json`.

Todo JSON de esos directorios, salvo el propio manifiesto, debe aparecer exactamente una vez.

Un nuevo archivo no registrado hace fallar CI.

## Rutas privadas

Las rutas locales reservadas incluyen:

- `private_cases/`;
- `local_cases/`;
- `.almas-private/`;
- `private_holdouts/`;
- `validation/private/`;
- `holdouts/private/`;
- `data/private/`.

Además de estar ignoradas por Git, el contrato público falla si cualquiera de ellas aparece físicamente en el checkout auditado.

## Payloads públicos

La guardia recursiva rechaza claves explícitamente privadas como:

- `private_case_data`;
- `private_message`;
- `private_correspondence`;
- `private_birth_data`;
- `private_report`;
- `medical_record`.

La detección por claves es una barrera adicional, no una afirmación de que cualquier payload que la supere sea necesariamente anónimo.

La obligación primaria sigue siendo la clasificación y procedencia correcta.

## Validación privada y publicación

Un caso privado puede utilizarse fuera del repositorio para investigación o validación cuando exista una base legítima para hacerlo.

Pero:

- no puede convertirse en fixture público;
- no puede transformarse en caso público mediante pseudónimo;
- no puede usarse como holdout público;
- una regla obtenida de él debe generalizarse y validarse independientemente;
- su resultado individual no debe publicarse como evidencia confirmatoria.

## PRIVACY_BREACH

Se registra `PRIVACY_BREACH` cuando material no público entra en un corpus, fixture, ejemplo, holdout o artefacto público.

Cualquier breach invalida ese artefacto para validación pública y exige retirar los datos afectados de la rama/release antes de continuar.

## Relación con L3

Un discriminador puede superar todos los gates estadísticos y seguir sin ser publicable si su validación expone datos privados.

Privacidad y capacidad discriminante son gates independientes.

## Estado de cierre

El Paso 20 audita esta política junto con el resto de la rama para la release 1.12.0. La privacidad permanece como gate independiente: el cierre de versión no promueve discriminadores ni elimina limitaciones de validación pendientes.
