"""Synthetic provenance failures must block protected access."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import freeze_manifest as fm


class FreezeManifest(unittest.TestCase):
    def test_python_drift_blocks_access_with_unchanged_packages(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            doc = {"files": {}, "built_from_commit": "unused-with-no-files",
                   "likelihood_grids": {"aggregate_sha256": "empty"},
                   "environment_observed": {"evaluation_python": "Python 3.12.0", "evaluation_venv_packages": ["numpy==1.0"]}}
            path.write_text(json.dumps(doc))
            observed = {"evaluation_python": "Python 3.13.16", "evaluation_venv_packages": ["numpy==1.0"]}
            with patch.object(fm, "MANIFEST", path), patch.object(fm, "grid_records", return_value=({}, "empty", {})), \
                    patch.object(fm, "checks", return_value={"synthetic": True}), \
                    patch.object(fm, "environment_observed", return_value=observed):
                self.assertIn("evaluation Python differs from the frozen version", fm.verify(quiet=True))
                with self.assertRaises(SystemExit):
                    fm.check_for_access({"freeze_manifest_sha256": fm.sha(path)})
                doc["environment_observed"] = observed
                path.write_text(json.dumps(doc))
                self.assertEqual(fm.verify(quiet=True), [])

    def test_source_commit_must_contain_the_recorded_bytes(self):
        rel = "scripts/acceptance.py"
        groups = {"code": {rel: {"sha256": fm.sha(ROOT / rel), "in_repository": True}}}
        self.assertEqual(fm.source_commit_mismatches(groups, "HEAD"), [])
        groups["code"][rel]["sha256"] = "0" * 64
        self.assertEqual(fm.source_commit_mismatches(groups, "HEAD"), [rel])
        self.assertEqual(fm.source_commit_mismatches(groups, "missing-synthetic-revision"), [rel])


if __name__ == "__main__":
    unittest.main()
