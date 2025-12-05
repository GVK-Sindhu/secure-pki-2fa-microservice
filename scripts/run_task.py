from datetime import datetime

with open("/data/cron.log", "a") as f:
    f.write(f"Cron executed at {datetime.utcnow()}\n")
