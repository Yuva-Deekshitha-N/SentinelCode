# clean.py — no secrets, no leaks

def add(a, b):
    return a + b

def greet(name):
    return f"Hello, {name}"

with open("data.txt", "r") as f:
    data = f.read()
