import json

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

    return data

