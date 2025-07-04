from pymongo import MongoClient
import json
import csv
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

# Connect to MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")  # Access 'MONGODB_URI' from .env
client = MongoClient(MONGODB_URI)       # Making a Connection with MongoClient

# Create database "scraped_books"
db = client.scraped_books

# Get collection/table "change_log" 
change_log = db["change_log"]

def write_daily_change_report():
    # Output directory
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)

    # Create filename with datetime-stamp 
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    json_filename = os.path.join(output_dir, f"change_report_{date_str}.json")
    # csv_filename = os.path.join(output_dir, f"change_report_{date_str}.csv")

    # Fetch today's time stamp from "change_log" colelction from mongoDB
    changes = list(change_log.find({"timestamp": {"$regex": f"^{date_str}"}}))

    # Changes - write in JSON
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(changes, f, indent=4, default=str)
    print(f"JSON report saved: {json_filename}")

# If run directly
if __name__ == "__main__":
    write_daily_change_report()