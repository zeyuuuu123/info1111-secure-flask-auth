"""Baseline authentication/security checks.

Run this script from the repository root at the baseline-review stage, before
the later password recovery and route-protection fixes are applied.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


app.app.config.update(TESTING=True)
client = app.app.test_client()

checks = []

pw_text = app.PASSWORDS_FILE.read_text(encoding="utf-8")
checks.append(("plaintext_password_file", "tjones01:tjones01123" in pw_text))

forgot = client.get("/forgot")
checks.append(("forgot_discloses_password_file", forgot.status_code == 200 and b"tjones01:" in forgot.data))

profile_logged_out = client.get("/profile")
checks.append(("profile_logged_out_not_redirected", profile_logged_out.status_code == 200))

profiles_logged_out = client.get("/profiles")
checks.append(("profiles_logged_out_accessible", profiles_logged_out.status_code == 200))

login = client.post("/login", data={"username": "tjones01", "password": "tjones01123"})
checks.append(("plaintext_login_succeeds", login.status_code in (302, 303)))

other_profile = client.get("/profile/mscott01")
checks.append(("cross_user_profile_route_accessible", other_profile.status_code == 200))

for name, result in checks:
    print(f"{name}: {'OBSERVED' if result else 'NOT_OBSERVED'}")
print("forgot_status:", forgot.status_code)
print("profile_logged_out_status:", profile_logged_out.status_code)
print("profiles_logged_out_status:", profiles_logged_out.status_code)
print("other_profile_status:", other_profile.status_code)
