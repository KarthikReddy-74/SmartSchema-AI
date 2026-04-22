from datetime import datetime

def log_change(msg):
    with open("evolution.log", "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")