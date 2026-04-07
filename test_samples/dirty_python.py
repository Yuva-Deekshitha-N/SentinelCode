# dirty_python.py — has secrets, leaks, and sensitive variable names

import sqlite3
import socket

# Hardcoded AWS key
aws_key = "AKIAIOSFODNN7EXAMPLE"

# Hardcoded password
password = "supersecret123"

# GitHub token
github_token = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456abcd"

# Google API key
google_key = "AIzaSyD-9tSrke72I6hDl53b2yhsQ0T9H8ntxyz"

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
api_key = "something"
secret = "hidden"
credential = "admin:pass"
