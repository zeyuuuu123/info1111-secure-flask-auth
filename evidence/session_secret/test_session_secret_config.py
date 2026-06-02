"""Session secret configuration verification checks."""

from pathlib import Path
import importlib
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def load_app_with_secret(secret_value):
    if secret_value is None:
        os.environ.pop("SECRET_KEY", None)
    else:
        os.environ["SECRET_KEY"] = secret_value

    if "app" in sys.modules:
        del sys.modules["app"]
    return importlib.import_module("app")


source = (ROOT / "app.py").read_text(encoding="utf-8")
gitignore_lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

print("SK_source_contains_hard_coded_dev_secret:", "app.secret_key = 'dev-secret-key'" in source)
print("SK_source_reads_secret_key_env:", "SECRET_KEY" in source and "os.getenv" in source)
print("SK_env_example_exists:", (ROOT / ".env.example").exists())
print("SK_env_file_ignored_in_gitignore:", ".env" in gitignore_lines)

configured = load_app_with_secret("test-secret-from-environment")
print("SK_configured_runtime_secret_key:", configured.app.secret_key)

fallback = load_app_with_secret(None)
print("SK_fallback_runtime_secret_key:", fallback.app.secret_key)
