import logging
import os
import yaml

from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = "config.yaml"

class Utils:

    def get_config_values() -> dict[str, str]:
        """
        Reads a yaml config file for the current file and returns its values

        Raises:
            Exception: When yaml file is not present.

        Returns:
            dict[str, str]: Key-value pairs of config items
        """

        yaml_file_path = os.path.dirname(os.path.dirname(__file__)) + "/" + CONFIG_FILE_NAME

        # retrieve config values from yaml file
        if Path(yaml_file_path).exists:
            with open(yaml_file_path, encoding='utf-8') as yaml_file:
                yaml_config = yaml.safe_load(yaml_file)
        else:
            raise Exception(f"Missing {yaml_file_path} file.")
        
        config_values = {}

        log_level = yaml_config.get("logging").get("log_level")
        animal_api_url = yaml_config.get("animal_api_url")

        config_values = config_values | { "log_level": log_level } | { "animal_api_url": animal_api_url }

        return config_values


    def override_root_level_log_level(log_level: str, logger_name: str):
        """
        Overrides the root log level

        Args:
            log_level (str): Log level
            logger_name (str): Logger name
        """

        logging.getLogger(logger_name).setLevel(logging._nameToLevel[log_level])