import json


DEFAULTS = {
  "highscore_filename": "highscores.json",
  "seed": 42,
  "level_max_time": 90,
  "lives": 3,
  "pacgum": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200
}

def remove_comments(text: str) -> str:
    cleaned_txt = []
    for line in text.splitlines():
        if not line.strip().startswith("#"):
            cleaned_txt.append(line.strip())

    return "\n".join(cleaned_txt)

def load_config(config_path: str) -> dict:
    try:
        with open(config_path) as file:
            raw = remove_comments(file.read())
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Config Error: {e}, using defaults")
        data = {}

    config = DEFAULTS.copy()
    for key, default in DEFAULTS.items():
        value = data.get(key, default)
        if key in {"level_max_time", "lives", "pacgum"}:
            if isinstance(value, int) and value > 0:
                config[key] = value
            else:
                print(f"Config Error: {key} must be > 0, using default")
                config[key] = default

        elif key in {"points_per_pacgum", "points_per_super_pacgum", "points_per_ghost"}:
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
                print(f"Config Error: {key} must be a non-empty .json file, using default")
                config[key] = default

    return config


print(load_config("../config.json"))

