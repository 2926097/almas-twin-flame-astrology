import json
import unittest
from pathlib import Path

from almas_tfa.ontological_discriminator import discriminate_ontology


ROOT = Path(__file__).resolve().parents[1]


def _type_matches(value, expected):
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    raise AssertionError(f"Tipo JSON Schema no soportado por el test: {expected}")


def assert_schema(instance, schema, path="$"):
    if "const" in schema:
        assert instance == schema["const"], (
            f"{path}: valor {instance!r} != const {schema['const']!r}"
        )

    if "enum" in schema:
        assert instance in schema["enum"], (
            f"{path}: valor {instance!r} fuera de enum {schema['enum']!r}"
        )

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = (
            expected_type if isinstance(expected_type, list) else [expected_type]
        )
        assert any(_type_matches(instance, item) for item in expected_types), (
            f"{path}: tipo incompatible con {expected_types!r}"
        )

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            assert key in instance, f"{path}: falta propiedad requerida {key!r}"

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)

        for key, value in instance.items():
            if key in properties:
                assert_schema(value, properties[key], f"{path}.{key}")
            elif additional is False:
                raise AssertionError(
                    f"{path}: propiedad adicional no permitida {key!r}"
                )
            elif isinstance(additional, dict):
                assert_schema(value, additional, f"{path}.{key}")

    if isinstance(instance, list):
        if "minItems" in schema:
            assert len(instance) >= schema["minItems"], (
                f"{path}: menos elementos que minItems"
            )
        if "maxItems" in schema:
            assert len(instance) <= schema["maxItems"], (
                f"{path}: más elementos que maxItems"
            )
        if schema.get("uniqueItems"):
            serialized = [
                json.dumps(item, sort_keys=True, ensure_ascii=False)
                for item in instance
            ]
            assert len(serialized) == len(set(serialized)), (
                f"{path}: uniqueItems violado"
            )

        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                assert_schema(item, item_schema, f"{path}[{index}]")


class TestOntologicalDiscriminatorSchema(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "schemas/ontological-discriminator-output.schema.json")
            .read_text(encoding="utf-8")
        )

    def test_confirmatory_output_matches_schema(self):
        output = discriminate_ontology(
            [
                {
                    "discriminator_id": "L3-SM",
                    "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                    "validation_level": "L3_VALIDATED",
                    "result": "SEPARATES",
                    "excluded_model": "SOULMATE_MODEL",
                    "root_key": "ROOT_L3",
                }
            ]
        )
        assert_schema(output, self.schema)

    def test_exploratory_output_matches_schema(self):
        output = discriminate_ontology(
            [
                {
                    "discriminator_id": "OD01",
                    "pair": ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
                    "validation_level": "L2_EXPERIMENTAL",
                    "result": "SEPARATES",
                    "excluded_model": "SOULMATE_MODEL",
                    "root_key": "ROOT_L2",
                }
            ],
            mode="EXPLORATORY",
        )
        assert_schema(output, self.schema)


if __name__ == "__main__":
    unittest.main()
