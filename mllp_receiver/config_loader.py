import json
import logging

logger = logging.getLogger("mllp_receiver")


def load_config(filepath="config.json"):
    """Load and validate listener configuration from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise

    app_config = config.get("application", {})
    listeners = config.get("listeners", [])

    valid_listeners = []
    for listener in listeners:
        if validate_listener(listener):
            valid_listeners.append(listener)
        else:
            logger.error(f"Invalid listener configuration skipped: {listener}")

    logger.info(f"Loaded {len(valid_listeners)} valid listener(s) out of {len(listeners)} configured")
    return app_config, valid_listeners


def validate_listener(listener):
    """Check that a listener config has the required fields."""
    required_fields = ["name", "ipAddress", "port"]
    for field in required_fields:
        if field not in listener:
            logger.error(f"Listener missing required field '{field}': {listener}")
            return False

    if not isinstance(listener["port"], int):
        logger.error(f"Listener port must be an integer: {listener}")
        return False

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app_config, listeners = load_config()
    print(f"\nApplication config: {app_config}")
    print(f"\nValid listeners:")
    for l in listeners:
        print(f"  {l}")