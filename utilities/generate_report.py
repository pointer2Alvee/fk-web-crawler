from pymongo import MongoClient
import json
import csv
import os
from datetime import datetime, timezone

# Making a Connection with MongoClient
client = MongoClient("mongodb+srv://fkcrawler_Alvee:fk1234@fkwebcrawler.ozzbwx0.mongodb.net/")
db = client.scraped_books
change_log = db["change_log"]

# Output directory
output_dir = "reports"
os.makedirs(output_dir, exist_ok=True)

# Create filename with datetime-stamp 
date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
json_filename = os.path.join(output_dir, f"change_report_{date_str}.json")
csv_filename = os.path.join(output_dir, f"change_report_{date_str}.csv")

# Fetch today's time stamp from "change_log" colelction from mongoDB
changes = list(change_log.find({"timestamp": {"$regex": f"^{date_str}"}}))

# Changes - write in JSON
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(changes, f, indent=4, default=str)
print(f"JSON report saved: {json_filename}")