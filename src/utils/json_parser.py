import json


def save_state(data, filename="src/utils/state.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def load_state(filename="src/utils/state.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
