"""Legacy compatibility presets.
The active product uses app.factory_catalog instead.
"""
PRESETS = {}
MODE_LABELS = {"safe": "Brand-safe"}

def get_presets_for_mode(mode: str = "safe") -> dict:
    return {}

def build_prompt(persona_base: str, preset_key: str) -> str:
    return persona_base
