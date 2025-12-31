import datetime
import json
from pathlib import Path
from typing import Dict, List

LOG_FILE = Path("/app/backend/data/logs.json")

def ensure_log_file():
    """Ensure log file and directory exist."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text(json.dumps([]))

def log_event(event: str, data: Dict):
    """Log an event to console and file.
    
    Args:
        event: Event type (e.g., LEAD_SCORED, EMAIL_SENT)
        data: Event data dictionary
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "event": event,
        "data": data
    }
    
    # Print to console
    print(f"[{timestamp}] {event} | {data}")
    
    # Write to log file
    try:
        ensure_log_file()
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        
        logs.append(log_entry)
        
        # Keep only last 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def get_logs(limit: int = 100) -> List[Dict]:
    """Retrieve recent logs.
    
    Args:
        limit: Maximum number of logs to return
        
    Returns:
        List of log entries
    """
    try:
        ensure_log_file()
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        return logs[-limit:]
    except Exception as e:
        print(f"Error reading log file: {e}")
        return []

def clear_logs():
    """Clear all logs."""
    try:
        ensure_log_file()
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)
    except Exception as e:
        print(f"Error clearing logs: {e}")
