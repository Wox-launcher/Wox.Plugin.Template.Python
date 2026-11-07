"""Sync the bundled skills from the Wox repository."""

from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ("wox-plugin-creator", "wox-plugin-submit2store")


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        upstream = Path(temp_dir) / "wox"
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
             "https://github.com/Wox-launcher/Wox.git", str(upstream)],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(upstream), "sparse-checkout", "set",
             *(f".agents/skills/{name}" for name in SKILLS)],
            check=True,
        )
        source = upstream / ".agents" / "skills"
        for name in SKILLS:
            if not (source / name).is_dir():
                raise FileNotFoundError(f"Upstream skill not found: {name}")
        target = ROOT / ".agents" / "skills"
        target.mkdir(parents=True, exist_ok=True)
        for name in SKILLS:
            if (target / name).exists():
                shutil.rmtree(target / name)
            shutil.copytree(source / name, target / name)
            print(f"Synced {name}")


if __name__ == "__main__":
    main()
