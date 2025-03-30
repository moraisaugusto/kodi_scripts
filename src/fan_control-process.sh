#! /bin/sh

### BEGIN INIT INFO
# Provides:          fan_control.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
### END INIT INFO

# Define the path to the fancontrol script
FANCONTROL_SCRIPT="/storage/.config/fan_control.py"

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting fan_control.py..."
    if ! pgrep -f "$FANCONTROL_SCRIPT" > /dev/null; then
      # Only start if not already running
      nohup python3 "$FANCONTROL_SCRIPT" &> /dev/null &
      echo "fan_control.py started successfully."
    else
      echo "fan_control.py is already running."
    fi
    ;;
  stop)
    echo "Stopping fan_control.py..."
    pkill -f "$FANCONTROL_SCRIPT"
    if [ $? -eq 0 ]; then
      echo "fan_control.py stopped successfully."
    else
      echo "Failed to stop fan_control.py. It may not be running."
    fi
    ;;
  restart)
    echo "Restarting fan_control.py..."
    $0 stop
    $0 start
    ;;
  status)
    if pgrep -f "$FANCONTROL_SCRIPT" > /dev/null; then
      echo "fan_control.py is running."
    else
      echo "fan_control.py is not running."
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0
