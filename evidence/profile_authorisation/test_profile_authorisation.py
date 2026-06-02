"""Profile ownership authorisation verification checks."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


app.app.config.update(TESTING=True)

user_a = "authza01"
pass_a = "AuthzA01!"
user_b = "authzb01"
pass_b = "AuthzB01!"

client = app.app.test_client()
client.post(
    "/signup",
    data={
        "name": "Authorisation User A",
        "username": user_a,
        "password": pass_a,
        "classes": "INFO1111",
        "dob": "01/01/2000",
        "address": "Test Address A",
        "availability": "Mon 09:00-10:00",
    },
)

setup_client = app.app.test_client()
setup_client.post(
    "/signup",
    data={
        "name": "Authorisation User B",
        "username": user_b,
        "password": pass_b,
        "classes": "INFO1111",
        "dob": "02/02/2000",
        "address": "Test Address B",
        "availability": "Tue 09:00-10:00",
    },
)

client.post("/login", data={"username": user_a, "password": pass_a})
other_profile = client.get(f"/profile/{user_b}")
own_profile = client.get(f"/profile/{user_a}")
logged_out = app.app.test_client().get(f"/profile/{user_a}")

print("PA_cross_user_profile:", f"status={other_profile.status_code}, location={other_profile.headers.get('Location') or 'none'}")
print("PA_own_profile:", f"status={own_profile.status_code}, location={own_profile.headers.get('Location') or 'none'}")
print("PA_logged_out_profile:", f"status={logged_out.status_code}, location={logged_out.headers.get('Location') or 'none'}")
