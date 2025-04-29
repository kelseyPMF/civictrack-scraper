import datetime

def log_error(message):
    with open("scraper_errors.log", "a") as f:
        timestamp = datetime.datetime.now().isoformat()
        f.write(f"[{timestamp}] {message}\n")
