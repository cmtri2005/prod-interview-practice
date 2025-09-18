import json

with open("/mnt/d/Desktop/Desktop/MLOps/prod-interview-practice/details.json", "r", encoding="utf-8") as f:
    print(json.load(f)[9])