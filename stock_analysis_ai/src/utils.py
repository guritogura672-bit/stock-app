import yaml
import os
import yaml
import os
import sys

def load_config(config_path="config.yaml"):
    """
    Loads configuration from a YAML file.
    Prioritizes file in current directory.
    Falls back to internal bundled config if running as EXE.
    """
    # 1. Check current working directory (User overrides)
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # 2. Check parent directory (Dev mode)
    parent_path = os.path.join("..", config_path)
    if os.path.exists(parent_path):
        with open(parent_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    # 3. Check MEIPASS (PyInstaller Bundled)
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        bundled_path = os.path.join(bundle_dir, config_path)
        if os.path.exists(bundled_path):
            with open(bundled_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

    raise FileNotFoundError(f"Config file not found: {config_path}")

def save_config(config, config_path="config.yaml"):
    """
    Saves the configuration dictionary to a YAML file.
    """
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
