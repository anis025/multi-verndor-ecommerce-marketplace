import os, json, urllib.request

data = json.dumps({"email": "mdanis.dev@gmail.com"}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/admin/auth/login",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=5) as r:
        print("LOGIN   ->", r.status, r.read().decode())
except urllib.error.HTTPError as e:
    print("LOGIN   ->", e.code, e.read().decode())
