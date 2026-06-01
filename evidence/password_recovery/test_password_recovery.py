"""Password recovery no-disclosure verification checks."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


app.app.config.update(TESTING=True)
client = app.app.test_client()

get_resp = client.get("/forgot")
existing_resp = client.post("/forgot", data={"username": "tjones01"})
fake_resp = client.post("/forgot", data={"username": "doesnotexist01"})

request_log = ""
if app.PASSWORD_RESET_REQUESTS_FILE.exists():
    request_log = app.PASSWORD_RESET_REQUESTS_FILE.read_text(encoding="utf-8")

msg = b"If this account exists, a password reset request has been recorded."
credential_markers = [b"tjones01:", b"scrypt:", b"tjones01123"]

print("PR2 forgot_get_status:", get_resp.status_code)
print("PR2 forgot_get_has_form:", b"Request password reset" in get_resp.data)
print("PR2 forgot_get_discloses_credentials:", any(marker in get_resp.data for marker in credential_markers))
print("PR3 existing_user_status:", existing_resp.status_code)
print("PR3 existing_user_generic_message:", msg in existing_resp.data)
print("PR3 existing_user_discloses_credentials:", any(marker in existing_resp.data for marker in credential_markers))
print("PR4 fake_user_status:", fake_resp.status_code)
print("PR4 fake_user_same_generic_message:", msg in fake_resp.data)
print("PR4 fake_user_discloses_credentials:", any(marker in fake_resp.data for marker in credential_markers))
print("PR5 request_log_entries:", len([line for line in request_log.splitlines() if line.strip()]))
print("PR5 request_log_preview:")
for line in request_log.splitlines()[-2:]:
    print(line)
