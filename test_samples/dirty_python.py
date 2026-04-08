import os
# dirty_python.py — has secrets, leaks, and sensitive variable names

import sqlite3
import socket

# Hardcoded AWS key
aws_key = "os.environ["AWS_ACCESS_KEY_ID"]"

# Hardcoded password
password = os.environ["DB_PASSWORD"]

# GitHub token
github_token = "os.environ["GITHUB_TOKEN"]"

# Google API key
google_key = "os.environ["GOOGLE_API_KEY"]"

# MongoDB URL with credentials
db_url = "mongodb://admin:password123@localhost:27017/mydb"

# Unclosed DB connection
conn = sqlite3.connect("mydb.db")

# Unclosed file
f = open("data.txt", "r")
data = f.read()

# Unclosed socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Sensitive variable names (NLP)
token = "some_value"
api_key = os.environ["API_KEY"]
secret = "hidden"
credential = "admin:pass"