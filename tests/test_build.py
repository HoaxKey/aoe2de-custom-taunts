from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("taunt_build", ROOT / "scripts" / "build.py")
assert SPEC and SPEC.loader
build_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_module
SPEC.loader.exec_module(build_module)


def payload() -> dict:
    return {
        "schema_version": 1,
        "mod": {
            "slug": "test-taunts",
            "title": "Test Taunts",
            "author": "Test",
            "version": "1.0.0",
            "description": "Test package",
            "custom_number_start": 300,
        },
        "taunts": [
            {
                "number": 300,
                "display_name": "Test",
                "source_audio": "test.wav",
                "output_filename": "Play_Taunt_300.wem",
            }
        ],
    }


class BuildTests(unittest.TestCase):
    def make_project(self, temporary: Path, data: dict | None = None):
        source_dir = temporary / "source"
        source_dir.mkdir()
        (source_dir / "test.wav").write_bytes(b"source")
        manifest = temporary / "taunts.json"
        manifest.write_text(json.dumps(data or payload()), encoding="utf-8")
        return build_module.load_project(manifest, source_dir), source_dir

    def test_duplicate_number_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            data = payload()
            data["taunts"].append(dict(data["taunts"][0]))
            with self.assertRaisesRegex(build_module.ValidationError, "duplicate taunt number"):
                self.make_project(temporary, data)

    def test_number_below_custom_range_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            data = payload()
            data["taunts"][0]["number"] = 299
            data["taunts"][0]["output_filename"] = "Play_Taunt_299.wem"
            with self.assertRaisesRegex(build_module.ValidationError, "between 300"):
                self.make_project(temporary, data)

    def test_output_name_must_match_number(self):
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            data = payload()
            data["taunts"][0]["output_filename"] = "wrong.wem"
            with self.assertRaisesRegex(build_module.ValidationError, "must be exactly Play_Taunt_300.wem"):
                self.make_project(temporary, data)

    def test_unsafe_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            data = payload()
            data["mod"]["version"] = "../../escape"
            with self.assertRaisesRegex(build_module.ValidationError, "unsafe filename"):
                self.make_project(temporary, data)

    def test_strict_build_rejects_missing_wem(self):
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            project, _source = self.make_project(temporary)
            wem_dir = temporary / "wem"
            wem_dir.mkdir()
            with self.assertRaisesRegex(build_module.ValidationError, "required Wwise files are missing"):
                build_module.build(project, wem_dir, temporary / "build", temporary / "release", False)

    def test_complete_build_has_exact_game_path(self):
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            project, _source = self.make_project(temporary)
            wem_dir = temporary / "wem"
            wem_dir.mkdir()
            # Minimal structural fixture, not represented as playable audio.
            fixture = b"RIFF" + (40).to_bytes(4, "little") + b"WAVE" + b"\0" * 36
            (wem_dir / "Play_Taunt_300.wem").write_bytes(fixture)
            archive = build_module.build(project, wem_dir, temporary / "build", temporary / "release", False)
            with zipfile.ZipFile(archive) as package:
                self.assertIn("resources/_common/drs/sounds/Play_Taunt_300.wem", package.namelist())
                self.assertIn("info.json", package.namelist())
                self.assertIn("TAUNTS.md", package.namelist())


if __name__ == "__main__":
    unittest.main()
