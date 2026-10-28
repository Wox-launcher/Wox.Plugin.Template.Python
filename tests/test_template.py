import importlib.util
import json
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
