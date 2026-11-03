import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestTemplate(unittest.TestCase):
    def test_manual_initialization_detects_template(self):
        init = load_module("init_wox_project", ROOT / "scripts/init-wox-project.py")
        data = init.load_plugin_data()
        if "{{." + "PluginID}}" in (ROOT / "plugin.json").read_text(encoding="utf-8"):
            self.assertFalse(init.is_initialized(data))
        else:
            self.assertTrue(init.is_initialized(data))
        self.assertEqual(init.package_name_from_plugin_name("My Plugin!"), "my-plugin")

    def test_scaffolder_renders_metadata(self):
        scaffold = load_module("scaffold", ROOT / ".agents/skills/wox-plugin-creator/scripts/scaffold_wox_plugin.py")
        content = (ROOT / "plugin.json").read_text(encoding="utf-8")
        if "{{." + "TriggerKeywordsJSON}}" not in content:
            self.skipTest("Template has already been initialized")
        data = json.loads(scaffold.render_template(content, {
            "PluginID": "test-id", "Name": "Test", "Description": "Example",
            "Author": "Author", "TriggerKeywordsJSON": '["one", "two"]',
        }))
        self.assertEqual(data["Id"], "test-id")
        self.assertEqual(data["TriggerKeywords"], ["one", "two"])
        self.assertNotIn("{{", json.dumps(data))

    def test_reinitialization_updates_package_name(self):
        scaffold = load_module("scaffold", ROOT / ".agents/skills/wox-plugin-creator/scripts/scaffold_wox_plugin.py")
        for scaffolded in (False, True):
            with self.subTest(scaffolded=scaffolded), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                (project / "scripts").mkdir()
                for name in ("plugin.json", "Makefile", "README.md", "scripts/init-wox-project.py"):
                    shutil.copy(ROOT / name, project / name)
                script = project / "scripts/init-wox-project.py"
                if scaffolded:
                    scaffold.apply_placeholders_in_tree(project, {
                        "PluginID": "test-id", "Name": "First Plugin", "Description": "Description",
                        "Author": "Author", "TriggerKeywordsJSON": '["first"]',
                    })
                else:
                    subprocess.run([sys.executable, str(script)], input="First Plugin\nDescription\nfirst\nAuthor\n\ny\n", text=True, check=True, capture_output=True)
                    self.assertIn("PLUGIN_NAME := first-plugin", (project / "Makefile").read_text())

                subprocess.run([sys.executable, str(script)], input="Second Plugin\n\n\n\n\ny\n", text=True, check=True, capture_output=True)
                makefile = (project / "Makefile").read_text()
                self.assertIn("PLUGIN_NAME := second-plugin", makefile)
                self.assertIn("wox.plugin.$(PLUGIN_NAME).wox", makefile)
                self.assertEqual(json.loads((project / "plugin.json").read_text(encoding="utf-8"))["Name"], "Second Plugin")
                self.assertIn("# Second Plugin", (project / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
