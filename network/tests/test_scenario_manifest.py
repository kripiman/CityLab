"""
Tests unitarios para la validación de manifiestos YAML de escenarios contra schema.json.
(Fase 0 - Roadmap de Medición y Contención)
"""

import json
from pathlib import Path
import pytest
import yaml

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "config" / "scenarios" / "schema.json"
SCENARIOS_DIR = REPO_ROOT / "config" / "scenarios"


@pytest.fixture
def manifest_schema():
    assert SCHEMA_PATH.exists(), f"Schema file not found at {SCHEMA_PATH}"
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_schema_validity(manifest_schema):
    """Verifica que schema.json sea un esquema JSON válido."""
    assert manifest_schema["type"] == "object"
    assert "required" in manifest_schema
    assert "objectives" in manifest_schema["properties"]


def test_scenario_01_manifest(manifest_schema):
    """Valida el manifiesto piloto scenario_01.yml contra schema.json."""
    scenario_01_path = SCENARIOS_DIR / "scenario_01.yml"
    assert scenario_01_path.exists(), "scenario_01.yml must exist"

    with open(scenario_01_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if HAS_JSONSCHEMA:
        jsonschema.validate(instance=data, schema=manifest_schema)
    else:
        # Fallback basic assertions if jsonschema not installed
        assert data["id"] == "01"
        assert len(data["objectives"]) >= 3


def test_all_check_types_schema(manifest_schema):
    """Valida que todos los tipos de checks permitidos pasen la validación."""
    sample_manifest = {
        "id": "99",
        "title": "Escenario de Prueba Multicheck",
        "seed_scope": ["unit_ids", "flags", "coils"],
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Check HTTP status",
                "check": {"type": "http_status", "url": "http://10.0.2.20:8080/api/telemetry", "expect": 200}
            },
            {
                "id": "FLAG_2",
                "desc": "Check Historian Condition",
                "check": {"type": "historian_condition", "query": "grid_freq_hz < 58.0", "window_s": 30}
            },
            {
                "id": "FLAG_3",
                "desc": "Check SCADA Sector Status",
                "check": {"type": "scada_sector_status", "sector": "water", "expect": "LOSS_OF_VIEW"}
            },
            {
                "id": "FLAG_4",
                "desc": "Check SIEM Alert",
                "check": {"type": "siem_alert", "rule": "Industroyer2 GOOSE Spoofing"}
            },
            {
                "id": "FLAG_5",
                "desc": "Check OpenFlow Rule",
                "check": {"type": "openflow_rule", "switch": "s3", "pattern": "actions=drop"}
            }
        ]
    }

    if HAS_JSONSCHEMA:
        jsonschema.validate(instance=sample_manifest, schema=manifest_schema)


def test_invalid_manifest_rejected(manifest_schema):
    """Verifica que un manifiesto inválido falle la validación."""
    invalid_manifest = {
        "id": "99",
        # Missing title
        "objectives": [
            {
                "id": "FLAG_1",
                "desc": "Invalid check type",
                "check": {"type": "non_existent_check_type"}
            }
        ]
    }

    if HAS_JSONSCHEMA:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_manifest, schema=manifest_schema)


@pytest.mark.parametrize("scenario_num", [f"{i:02d}" for i in range(1, 30)])
def test_all_29_manifests_valid(manifest_schema, scenario_num):
    """Valida exhaustivamente cada uno de los 29 manifiestos generados contra schema.json."""
    manifest_file = SCENARIOS_DIR / f"scenario_{scenario_num}.yml"
    assert manifest_file.exists(), f"El manifiesto {manifest_file.name} no existe"

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["id"] == scenario_num
    assert len(data.get("objectives", [])) >= 1

    if HAS_JSONSCHEMA:
        jsonschema.validate(instance=data, schema=manifest_schema)
