import os
from datetime import datetime
import json

# Path for heartbeat log
LOG_FILE = "heartbeat_log.json"

def log_heartbeat(status="success", message=""):
    """
    Log the current run's status with timestamp.
    status: "success" or "failure"
    message: optional descriptive text
    """
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "status": status,
        "message": message
    }

    # Read existing log
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    # Append new entry
    log_data.append(entry)

    # Save back to file
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)

    print(f"[{timestamp}] Heartbeat logged: {status} - {message}")


if __name__ == "__main__":
    log_heartbeat("success", "Manual test run completed")
