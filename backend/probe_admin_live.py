import json, urllib.request, urllib.error

for email in ['mdanis.dev@gmail.com', 'somebody-else@example.com', 'unknown@example.com', '']:
    data = json.dumps({'email': email}).encode()
    req = urllib.request.Request(
        'http://localhost:8000/api/admin/auth/login',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f'LOGIN  {email!r:35s} -> {r.status} {r.read().decode()[:80]}')
    except urllib.error.HTTPError as e:
        print(f'LOGIN  {email!r:35s} -> {e.code} {e.read().decode()[:80]}')
