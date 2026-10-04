# Auditoría ALMAS 1.26.0 · Motor Jyotiṣa Relacional R1

La evolución implementa el alcance depurado R1 sobre la base pública `b27164e6eac08de7681f750eabb183a58ed82e19`. El motor VED es observacional, optativo y separado del scoring anterior. No hay cambios de fórmulas, pesos, gates, ontología, proveedor MOIRA/JPL ni política congelada SSAR.

## Resultado técnico

Se incorporan cartas siderales con procedencia Swiss/Moshier, perfiles Lahiri/Raman/KP/Fagan/CUSTOM, nakṣatras/pādas, kārakas 7/8 con bloqueo de empates, D9 y Kārakāṃśa tipados, doce Arudhas con excepciones, AL/UL/A7 y segunda posición UL, Bhrigu Bindu, once upagrahas, Abhijit opcional y Vimśottarī a tres niveles. La matriz relaciona D1/D9 en cuatro direcciones y el tratamiento temporal conserva anclajes estructurales y contactos compartidos. Vivāha Sahama admite carta anual con recibo declarado del retorno.

La envolvente `vedic` es opcional en el schema canónico. La función de incorporación copia el objeto y preserva campos anteriores, rechaza sobrescrituras y bloquea pesos o estados promovidos. Los planetas AK/DK comparten dependencia con sus posiciones físicas; Rahu/Ketu comparten eje también en D9. Los puntos por signo no reciben grados físicos. Los tests comprueban esas restricciones y la continuidad de un canonical anterior.

Se ofrecen CLI JSON/informe español, configuración y registros empaquetados, fixtures documentales y sintéticos, sensibilidad al ayanāṃśa/hora, controles de corpus estratificados, ablación por familia y Shapley de cobertura. Shapley no mide importancia metafísica ni eficacia predictiva. Las cohortes reutilizan sujetos y no se presentan como observaciones independientes.

## Verificación local

Las **43 pruebas VED** pasan en Python 3.12 con el extra astronómico. Incluyen 108 límites de pāda, asignación D9 contrastada por una regla elemental independiente, ejemplos numéricos de Rao, dos sistemas kāraka, Arudhas, saldo daśā, controles de entradas/DST, schema, deduplicación, período temporal y firewall canónico. El script `validate_vedic_runtime.py` pasa con carta doble, evento, cuatro capas D1/D9 y sensibilidad de ambos sujetos. El contrato público 1.26.0 pasa; la suite SSAR congelada reproduce sus nueve ablaciones y controles con PASS.

La batería ampliada de regresión de **1.141 pruebas pasa** en Python 3.12 (591,624 s), incluidas las integraciones canónicas SSAR y sus nueve ablaciones M00–M31. Esta ejecución excluyó dos pruebas largas: `test_full_pipeline.TestFullPipelineSynthetic.test_m00_m31_complete_with_explicit_inputs` y `test_return_activation.ReturnsTests.test_complete_pipeline_preserves_core_and_report_gate`; no se declara PASS íntegro de la suite. Una ejecución general anterior se interrumpió con exit 139 mientras registraba el test completo de retornos, sin atribuir una causa no demostrada. Las pruebas específicas posteriores de compatibilidad del panel, privacidad y VED pasan. Las solicitudes del panel 1.25.0 y 1.26.0 conservan compatibilidad explícita. La comparación de conversión sideral y flags directos es interna a Swiss; no se declara validación astronómica contra dos motores independientes. El workflow `vedic.yml` está preparado para Python 3.10/3.12 con el extra. El usuario ha autorizado expresamente publicar la rama `codex/almas-1.26-jyotisha` en `2926097/almas-twin-flame-astrology` y abrir una PR; la verificación remota se informará en esa PR.

## Alcance condicionado y aplazado

Aṣṭakūṭa dispone de ocho componentes con estados explícitos y geometría lunar/Tara; no se implementa ni publica la puntuación completa de 36 puntos sin tablas y excepciones verificadas. IVED escalar permanece nulo y sin pesos. Prāṇapada, Yogatārās, Sahamas adicionales, Varṣaphala completo y cruces védico–asteroides quedan aplazados por el alcance R1. La función anual exige un recibo externo; no contiene un nuevo solver del retorno solar ni autentica por sí misma documentos externos. No se añade integración automática del frontend ni de DOCX/PDF.

El perfil Arudha implementa siete regentes sin resolver fuerza de corregencias. Los contactos relacionales y cruces D1/D9 son hipótesis ALMAS. La genealogía doctrinal de Bhrigu Bindu no se declara resuelta. Estas restricciones son decisiones explícitas de depuración y no se ocultan como técnicas completadas.

## Estado empírico

Validación externa `NOT_PERFORMED`; capacidad discriminante `NOT_EVALUABLE`; clasificación de origen metafísico desde VED `INSUFFICIENT`; efecto canónico cero. Los controles sintéticos, pruebas unitarias, corrección BH y fixtures históricos numéricos no prueban eficacia empírica ni ontologías. No se incorporan datos de casos privados al repositorio público ni se redistribuyen los PDF consultados.
