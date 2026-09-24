import json


DEFAULTS = {
  "highscore_filename": "highscores.json",
  "seed": 42,
  "level_max_time": 90,
  "lives": 3,
  "pacgum": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "level": [{"width": 15, "height": 15},
            {"width": 20, "height": 20},
            {"width": 30, "height": 30},
            {"width": 40, "height": 40},
            {"width": 55, "height": 55},
            {"width": 50, "height": 50},
            {"width": 45, "height": 45},
            {"width": 40, "height": 40},
            {"width": 55, "height": 55},
            {"width": 50, "height": 50},
            ]
}


def remove_comments(text: str) -> str:
    """Strip comment lines from raw config text.

    Args:
        text: the raw file content.

    Returns:
        The same text with comment lines removed.
    """
    cleaned_txt = []
    for line in text.splitlines():
        if not line.strip().startswith("#"):
            cleaned_txt.append(line)

    return "\n".join(cleaned_txt)


def is_valid_level_list(value: list) -> bool:
    """Check whether a value is a valid list of levels.

    Args:
        value: a list of {width, height} for each level.

    Returns:
        True if value satisfies level list requirements, False
        otherwise.
    """
    if not isinstance(value, list):
        return False
    if len(value) < 10:
        return False

    for item in value:
        if not isinstance(item, dict):
            return False
        width, height = item.get("width"), item.get("height")
        if not isinstance(width, int) or width <= 0:
            return False
        if not isinstance(height, int) or height <= 0:
            return False

    return True


def load_config(config_path: str) -> dict:
    """Load and validate the config file, falling back to safe defaults
    in any missing key or wrong value.

    Args:
        config_path: a path to the JSON config file.

    Returns:
        A dict containing every key in DEFAULTS, each holding
        either its validated value from the file or its default.
    """
    try:
        with open(config_path) as file:
            raw = remove_comments(file.read())
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Config Error: {e}, using defaults")
        return DEFAULTS.copy()

    config = DEFAULTS.copy()
    for key, default in DEFAULTS.items():
        value = data.get(key)

        if value is None:
            print(f"{key} is missing, using default")
            value = default

        if key in {"level_max_time", "lives", "pacgum"}:
            if isinstance(value, int) and value > 0:
                config[key] = value
            else:
                print(f"Config Error: {key} must be > 0, using default")
                config[key] = default

        elif key in {"points_per_pacgum", "points_per_super_pacgum",
                     "points_per_ghost"}:
            if isinstance(value, int) and value >= 0:
                config[key] = value
            else:
                print(f"Config Error: {key} must be >= 0, using default")
                config[key] = default
        elif key == "seed":
            if isinstance(value, int):
                config[key] = value
            else:
                print(f"Config Error: {key} must be a number, using default")
                config[key] = default
        elif key == "highscore_filename":
            if isinstance(value, str) and value and value.endswith(".json"):
                config[key] = value
            else:
                print(f"Config Error: {key} must be a non-empty "
                      ".json file, using default")
                config[key] = default
        elif key == "level":
            if is_valid_level_list(value):
                config[key] = value
            else:
                print("Config Error: must be a list of 10 items of "
                      "{width, height} dict, using default")
                config[key] = default

    return config


print(load_config("./config.json"))
