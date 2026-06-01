"""Password hashing verification checks."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


app.app.config.update(TESTING=True)

client = app.app.test_client()
username = "hashscript01"
password = "HashScript01!"

client.post(
    "/signup",
    data={
        "name": "Hash Script User",
        "username": username,
        "password": password,
        "classes": "INFO1111",
        "dob": "01/01/2000",
        "address": "Test Address",
        "availability": "Mon 09:00-10:00",
    },
)

stored_lines = app.PASSWORDS_FILE.read_text(encoding="utf-8").splitlines()
stored_line = [line for line in stored_lines if line.startswith(f"{username}:")][-1]
stored_value = stored_line.split(":", 1)[1]
ph1 = password not in stored_line and stored_value.startswith(("scrypt:", "pbkdf2:"))

login_client = app.app.test_client()
correct = login_client.post("/login", data={"username": username, "password": password})
with login_client.session_transaction() as sess:
    ph2 = correct.status_code in (302, 303) and sess.get("username") == username

bad_client = app.app.test_client()
wrong = bad_client.post("/login", data={"username": username, "password": "wrong-password"})
with bad_client.session_transaction() as sess:
    ph3 = wrong.status_code == 200 and sess.get("username") is None and b"Invalid credentials" in wrong.data

print(f"PH1 stored_password_is_hash: {'PASS' if ph1 else 'FAIL'}")
print(f"PH2 correct_password_login: {'PASS' if ph2 else 'FAIL'}")
print(f"PH3 wrong_password_rejected: {'PASS' if ph3 else 'FAIL'}")
print("stored_prefix:", stored_value.split("$", 1)[0])
print("correct_login_status:", correct.status_code)
print("wrong_login_status:", wrong.status_code)
