"""Teste HTTP real, sem dependencias Python externas."""
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from http.client import HTTPException

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"


def request(path, method="GET", body=None, expected=200):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        response = urlopen(req, timeout=5)
    except HTTPError as error:
        response = error
    assert response.status == expected, (path, expected, response.status)
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Cache-Control") == "no-store"
    assert "default-src 'none'" in response.headers.get("Content-Security-Policy", "")
    text = response.read()
    return json.loads(text) if text else None


for attempt in range(60):
    try:
        assert request("/api/health")["status"] == "UP"
        break
    except (URLError, TimeoutError, ConnectionError, HTTPException):
        time.sleep(1)
else:
    raise SystemExit("API nao ficou pronta em 60 segundos")
request("/api/tasks")
task = request("/api/tasks", "POST", {"title": "Demonstrar pipeline", "description": "smoke"}, 201)
request("/api/tasks/" + task["id"])
request("/api/tasks/" + task["id"], "DELETE", expected=204)
request("/api/tasks/" + task["id"], expected=404)
request("/api/tasks", "POST", {"title": " "}, 400)
print("SMOKE PASS: health, list, create, get, delete, 404, validation, security headers")
