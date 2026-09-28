# Referencia planetaria independiente · Skyfield/DE440

ALMAS utiliza Skyfield exclusivamente como referencia independiente para el subgate planetario de la validación astronómica dorada. No es un segundo backend operativo del pipeline M00–M31.

## Contrato

La referencia queda fijada como `ALMAS_SKYFIELD_DE440_PLANETARY_REFERENCE_V1` sobre `skyfield==1.55`.

El runner exige un BSP local y su SHA-256 antes de abrirlo, utiliza los tiempos UTC de los casos preregistrados, observa los cuerpos desde el centro de la Tierra y aplica reducción aparente. Las longitudes y latitudes se expresan en la eclíptica y equinoccio verdaderos de fecha; la declinación se expresa respecto del ecuador y equinoccio verdaderos de fecha.

Se registra el target SPK efectivamente resuelto para cada cuerpo y se declara `network_io_used=false`.

## Cobertura

La referencia produce exactamente treinta medidas por caso: longitud, latitud y declinación para Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, Urano, Neptuno y Plutón.

No produce True Node, casas ni ángulos. Esas capas pertenecen a subgates independientes y no pueden completarse reutilizando Moira como referencia de sí mismo.

## Ejecución

```bash
pip install -e ".[astronomy-validation]"
python scripts/validate_skyfield_reference_runtime.py
python scripts/generate_skyfield_planetary_reference.py \
  --kernel /ruta/de440.bsp \
  --kernel-sha256 <sha256>
```

Los archivos generados son artefactos parciales de referencia. No deben presentarse como fixtures dorados completos hasta fusionarlos con las referencias independientes de True Node y casas/ángulos.

## Firewall

La ausencia de Skyfield no afecta al núcleo ALMAS. Cambiar la versión de Skyfield, la familia de kernel, el origen, el frame o la política de reducción exige una nueva versión del contrato de referencia.
