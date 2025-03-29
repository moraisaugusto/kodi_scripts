"""
Fan Control Script for Raspberry Pi

This script monitors the CPU temperature and controls a cooling fan using a GPIO pin.
It turns the fan on when the temperature exceeds a defined threshold and off when it falls below another threshold.

Dependencies:
    - `gpiozero` (Required for controlling GPIO pins. Install it via Kodi UI if missing.)
    - `vcgencmd` (Required for measuring CPU temperature.)

Configuration:
    - `ON_THRESHOLD` (int): Temperature (°C) to turn the fan on.
    - `OFF_THRESHOLD` (int): Temperature (°C) to turn the fan off.
    - `SLEEP_INTERVAL` (int): Time interval (seconds) between temperature checks.
    - `GPIO_PIN` (int): GPIO pin number used to control the fan.
    - `LOG_FILENAME` (str): Log file path.

Usage:
    Run the script with optional debugging enabled:
        python fan_control.py --debug

Raises:
    - RuntimeError: If temperature output cannot be parsed or thresholds are misconfigured.
"""

#!/usr/bin/env python3

import subprocess
import logging
import argparse
import time
import sys

try:
    sys.path.append("/storage/.kodi/addons/virtual.rpi-tools/lib")
    from gpiozero import OutputDevice
except ModuleNotFoundError:
    print("gpiozero Module not found, install it on kodi UI interface")

ON_THRESHOLD = 65  # (degrees Celsius) Fan kicks on at this temperature.
OFF_THRESHOLD = 55  # (degress Celsius) Fan shuts off at this temperature.
SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 23  # Which GPIO pin you're using to control the fan.
LOG_FILENAME = "/var/log/fan_control.log"


def get_temp():
    """Get the core temperature.
    Run a shell script to get the core temp and parse the output.
    Raises:
        RuntimeError: if response cannot be parsed.
    Returns:
        float: The core temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')


def setup_logger(debug=False):
    """Setup and configure the logger for both file and console output.
    
    Configures a logger named "app_logger" with logging level set to INFO. 
    Logs are written to a file specified by LOG_FILENAME with a formatter that includes 
    timestamp, log level, and message. If debug mode is enabled, logs are also printed 
    to the console.

    Args:
        debug (bool): Whether to enable console logging in addition to file logging.
            Defaults to False.

    Returns:
        logging.Logger: The configured logger instance ready for use.
    """
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_FILENAME)
    file_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    if debug:
        # Create a logger for console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)

    return logger


def main():
    """Run the script with optional debugging. Monitors CPU temperature and controls a fan based on predefined thresholds.
    
    The script uses command-line arguments to enable debug mode, which logs messages both to file and console.
    It continuously monitors the CPU temperature every SLEEP_INTERVAL seconds, turning the fan on if the
    temperature exceeds ON_THRESHOLD and turning it off when it drops below OFF_THRESHOLD.

    Args:
        None

    Returns:
        None

    Raises:
        RuntimeError: If OFF_THRESHOLD is not less than ON_THRESHOLD.

    Example:
        To run the script without debug mode:
            python script.py
        
        To run with debug mode enabled:
            python script.py --debug
    """
    parser = argparse.ArgumentParser(description="Run the script with optional debugging.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (log messages to console).")
    args = parser.parse_args()
    logger = setup_logger(debug=args.debug)

    # Create a logger for file logging
    if OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')


    fan = OutputDevice(GPIO_PIN)

    while True:
        temp = get_temp()
        logger.info(f"CPU temp: {temp}")

        # Start the fan if the temperature has reached the limit and the fan
        # isn't already running.
        # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
        if temp > ON_THRESHOLD and not fan.value:
            logger.warning("Turning on Fan")
            fan.on()

        # Stop the fan if the fan is running and the temperature has dropped
        # to 10 degrees below the limit.
        elif fan.value and temp < OFF_THRESHOLD:
            logger.warning("Turning off Fan")
            fan.off()

        time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    main()
