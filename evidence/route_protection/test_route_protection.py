"""Login-required route protection verification checks."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


app.app.config.update(TESTING=True)

protected_get = [
    "/profile",
    "/profiles",
    "/profiles/search?query=tjones01",
    "/bookings",
    "/bookings/new",
    "/inbox",
    "/availability",
]
public_get = ["/", "/login", "/signup", "/forgot"]

client = app.app.test_client()
print("RP1 logged_out_protected_routes:")
for route in protected_get:
    resp = client.get(route)
    print(f"{route}: status={resp.status_code}, location={resp.headers.get('Location') or 'none'}")

print("RP2 logged_out_public_routes:")
for route in public_get:
    resp = client.get(route)
    print(f"{route}: status={resp.status_code}")

login_client = app.app.test_client()
login_client.post(
    "/signup",
    data={
        "name": "Route Evidence User",
        "username": "routeevidence01",
        "password": "RouteEvidence01!",
        "classes": "INFO1111",
        "dob": "01/01/2000",
        "address": "Test Address",
        "availability": "Mon 09:00-10:00",
    },
)

print("RP3 logged_in_protected_routes:")
for route in ["/profile", "/profiles", "/bookings", "/bookings/new", "/inbox", "/availability"]:
    resp = login_client.get(route)
    print(f"{route}: status={resp.status_code}, location={resp.headers.get('Location') or 'none'}")

login_client.get("/logout")
after_logout = login_client.get("/profile")
print("RP4 after_logout_profile:", f"status={after_logout.status_code}, location={after_logout.headers.get('Location') or 'none'}")
