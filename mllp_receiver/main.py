import logging
import time

from mllp_receiver.logger_config import setup_logging
from mllp_receiver.config_loader import load_config
from mllp_receiver.listener import start_all_listeners


def main():
    app_config, listeners = load_config("config.json")

    log_level = app_config.get("logLevel", "INFO")
    logger = setup_logging(log_level)

    logger.info(f"Starting {app_config.get('name', 'MLLP Receiver')}")

    if not listeners:
        logger.error("No valid listeners configured. Exiting.")
        return

    threads = start_all_listeners(listeners)
    logger.info(f"All {len(threads)} listener(s) started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown requested. Exiting.")


if __name__ == "__main__":
    main()