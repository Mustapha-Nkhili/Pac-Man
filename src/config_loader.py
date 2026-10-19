import json
from typing import Any, TypeGuard

<<<<<<< HEAD
DEFAULTS = {
=======
DEFAULTS: dict[str, Any] = {
>>>>>>> origin/main
    "highscore_filename": "highscores.json",
    "seed": 42,
    "level_max_time": 90,
    "lives": 3,
<<<<<<< HEAD
    "pacgum": 42,
=======
    "pacgum": 10,
>>>>>>> origin/main
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "level": [
<<<<<<< HEAD
        {"width": 15, "height": 15},
        {"width": 20, "height": 20},
        {"width": 30, "height": 30},
        {"width": 40, "height": 40},
        {"width": 55, "height": 55},
        {"width": 50, "height": 50},
        {"width": 45, "height": 45},
        {"width": 40, "height": 40},
        {"width": 55, "height": 55},
        {"width": 50, "height": 50},
=======
        {"width": 11, "height": 7},
        {"width": 13, "height": 9},
        {"width": 15, "height": 9},
        {"width": 17, "height": 11},
        {"width": 19, "height": 11},
        {"width": 21, "height": 11},
        {"width": 21, "height": 13},
        {"width": 23, "height": 13},
        {"width": 25, "height": 13},
        {"width": 25, "height": 15},
>>>>>>> origin/main
    ],
}


class ConfigError(Exception):
    pass


class ConfigLoader:
    def _remove_comments(self, text: str) -> str:
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

    def _is_valid_int(self, value: Any) -> TypeGuard[int]:
        """Check whether a value is an int, excluding bool
        cause it a subtype of int

        Args:
            value: the value to check

        Returns:
            True if value is an int and not a bool, otherwise False
        """
        return isinstance(value, int) and not isinstance(value, bool)

    def _is_valid_level_list(self, value: list[Any]) -> bool:
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
            if not self._is_valid_int(width) or width <= 0:
                return False
            if not self._is_valid_int(height) or height <= 0:
                return False

            if height * width >= 1000:
                return False

        return True

    def load_config(self, config_path: str) -> dict[str, Any]:
        """Load and validate the config file, falling back to safe defaults
        in any missing key or wrong value.

        Args:
            config_path: a path to the JSON config file.

<<<<<<< HEAD
    if not isinstance(data, dict):
        print("Config Error: the config file must be a JSON object, " "using defaults")
        return DEFAULTS.copy()
=======
        Returns:
            A dict containing every key in DEFAULTS, each holding
            either its validated value from the file or its default.
        """
        try:
            with open(config_path) as file:
                raw = self._remove_comments(file.read())
            data = json.loads(raw)
        except OSError as e:
            raise ConfigError(f"Config Error: {e}")
        except json.JSONDecodeError as e:
            print(f"Config Error: {e}, using defaults")
            return DEFAULTS.copy()
>>>>>>> origin/main

        if not isinstance(data, dict):
            print(
                "Config Error: the config file must be a JSON object, "
                "using defaults"
            )
            return DEFAULTS.copy()

        config = DEFAULTS.copy()
        for key, default in DEFAULTS.items():
            value = data.get(key)

<<<<<<< HEAD
        if key in {"level_max_time", "lives", "pacgum"}:
            if is_valid_int(value) and value > 0:
                config[key] = value
            else:
                print(f"Config Error: {key} must be a number > 0, " "using default")
                config[key] = default

        elif key in {
            "points_per_pacgum",
            "points_per_super_pacgum",
            "points_per_ghost",
        }:
            if is_valid_int(value) and value >= 0:
                config[key] = value
            else:
                print(f"Config Error: {key} must be a number >= 0, " "using default")
                config[key] = default
        elif key == "seed":
            if is_valid_int(value):
                config[key] = value
            else:
                print(f"Config Error: {key} must be a number, using default")
                config[key] = default
        elif key == "highscore_filename":
            if isinstance(value, str) and value and value.endswith(".json"):
                config[key] = value
            else:
                print(
                    f"Config Error: {key} must be a non-empty "
                    ".json file, using default"
                )
                config[key] = default
        elif key == "level":
            if is_valid_level_list(value):
                config[key] = value
            else:
                print(
                    "Config Error: must be a list of 10 items of "
                    "{width, height} dict, using default"
                )
                config[key] = default
=======
            if value is None:
                print(f"{key} is missing, using default")
                value = default

            if key in {"level_max_time", "lives", "pacgum"}:
                if self._is_valid_int(value) and value > 0:
                    config[key] = value
                else:
                    print(
                        f"Config Error: {key} must be a number > 0, "
                        "using default"
                    )
                    config[key] = default
>>>>>>> origin/main

            elif key in {
                "points_per_pacgum",
                "points_per_super_pacgum",
                "points_per_ghost",
            }:
                if self._is_valid_int(value) and value >= 0:
                    config[key] = value
                else:
                    print(
                        f"Config Error: {key} must be a number >= 0, "
                        "using default"
                    )
                    config[key] = default
            elif key == "seed":
                if self._is_valid_int(value):
                    config[key] = value
                else:
                    print(
                        f"Config Error: {key} must be a number, using default"
                    )
                    config[key] = default
            elif key == "highscore_filename":
                if (
                    isinstance(value, str)
                    and value
                    and value.endswith(".json")
                ):
                    config[key] = value
                else:
                    print(
                        f"Config Error: {key} must be a non-empty "
                        ".json file, using default"
                    )
                    config[key] = default
            elif key == "level":
                if self._is_valid_level_list(value):
                    config[key] = value
                else:
                    print(
                        "Config Error: must be a list of 10 items of "
                        "{width, height} dict, using default"
                    )
                    config[key] = default

        return config
