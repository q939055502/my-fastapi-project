import os

import yaml


def load_response_msg() -> dict:
    config_path = os.path.join(
        os.path.dirname(__file__),
        "response_msg.yaml"
    )
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


RESPONSE_MSG = load_response_msg()
