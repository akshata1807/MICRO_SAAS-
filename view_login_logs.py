#!/usr/bin/env python3
"""
Script to view login activity logs
"""
import os
from datetime import datetime, timedelta

def view_login_logs(hours=24):
    """View login logs from the last X hours"""
    log_file = 'login_activity.log'

    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' does not exist yet.")
        print("Login activity will be logged here when users log in/out.")
        return

    print(f"=== LOGIN ACTIVITY LOGS (Last {hours} hours) ===")
    print(f"Log file: {os.path.abspath(log_file)}")
    print("-" * 60)

    threshold = datetime.now() - timedelta(hours=hours)

    with open(log_file, 'r') as f:
        lines = f.readlines()

    recent_logs = []
    for line in lines:
        if line.strip():
            # Parse the timestamp from the log line
            try:
                # Log format: 2025-09-14 06:42:34,567 - Login: User username (email) - IP: 127.0.0.1
                timestamp_str = line.split(' - ')[0]
                log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')

                if log_time >= threshold:
                    recent_logs.append(line.strip())
            except (ValueError, IndexError):
                # If we can't parse the timestamp, include the line anyway
                recent_logs.append(line.strip())

    if not recent_logs:
        print(f"No login activity in the last {hours} hours.")
    else:
        for log in recent_logs:
            print(log)

    print(f"\nTotal log entries in file: {len(lines)}")

def view_all_logs():
    """View all login logs"""
    log_file = 'login_activity.log'

    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' does not exist yet.")
        return

    print("=== ALL LOGIN ACTIVITY LOGS ===")
    print(f"Log file: {os.path.abspath(log_file)}")
    print("-" * 60)

    with open(log_file, 'r') as f:
        content = f.read()

    if content.strip():
        print(content)
    else:
        print("Log file is empty.")

def clear_logs():
    """Clear the login log file"""
    log_file = 'login_activity.log'

    if os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write("")
        print(f"Login logs cleared. File: {os.path.abspath(log_file)}")
    else:
        print("Log file does not exist.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'all':
            view_all_logs()
        elif command == 'clear':
            clear_logs()
        elif command.isdigit():
            view_login_logs(int(command))
        else:
            print("Usage: python view_login_logs.py [hours|all|clear]")
            print("  hours: Show logs from last X hours (default: 24)")
            print("  all: Show all logs")
            print("  clear: Clear all logs")
    else:
        view_login_logs(24)