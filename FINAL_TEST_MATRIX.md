# Final Test Matrix

## Summary

This matrix summarises the security behaviours tested after the implementation cycles. Each row links to the evidence file used to support the result.

| Area | Test ID | Behaviour tested | Evidence | Result |
| ---- | ------- | ---------------- | -------- | ------ |
| Baseline review | B1-B6 | Original authentication, password handling, recovery, route access, authorisation, and session-secret weaknesses were identified. | `evidence/baseline_review/baseline_review_results.txt` | Observed |
| Password hashing | PH1 | New stored passwords are Werkzeug hashes, not plaintext. | `evidence/password_hashing/password_hashing_results.txt`; `evidence/password_hashing/password_file_hash.png` | Pass |
| Password hashing | PH2 | A correct password still logs in successfully. | `evidence/password_hashing/password_hashing_results.txt`; `evidence/password_hashing/correct_login.png` | Pass |
| Password hashing | PH3 | An incorrect password is rejected. | `evidence/password_hashing/password_hashing_results.txt`; `evidence/password_hashing/wrong_login.png` | Pass |
| Password recovery | PR1 | Baseline `/forgot` route exposed credential data. | `evidence/password_recovery/baseline_forgot_disclosure.txt` | Observed |
| Password recovery | PR2 | `/forgot` now shows a reset-request form instead of the credential file. | `evidence/password_recovery/recovery_no_disclosure_results.txt` | Pass |
| Password recovery | PR3 | Submitting an existing username returns a generic no-disclosure message. | `evidence/password_recovery/recovery_no_disclosure_results.txt` | Pass |
| Password recovery | PR4 | Submitting a non-existing username returns the same generic no-disclosure message. | `evidence/password_recovery/recovery_no_disclosure_results.txt` | Pass |
| Password recovery | PR5 | Reset requests are recorded without exposing credentials in the response. | `evidence/password_recovery/recovery_no_disclosure_results.txt` | Pass |
| Route protection | RP1 | Logged-out users are redirected from protected routes to `/login`. | `evidence/route_protection/protected_route_results.txt` | Pass |
| Route protection | RP2 | Public routes remain accessible while logged out. | `evidence/route_protection/protected_route_results.txt` | Pass |
| Route protection | RP3 | Logged-in users can still access protected routes. | `evidence/route_protection/protected_route_results.txt` | Pass |
| Route protection | RP4 | Logout removes access to protected routes. | `evidence/route_protection/protected_route_results.txt` | Pass |
| Profile authorisation | PA1 | Baseline showed a logged-in user could reach another user's profile route. | `evidence/profile_authorisation/baseline_cross_user_profile_access.txt` | Observed |
| Profile authorisation | PA2 | A logged-in user cannot access another user's profile route after the fix. | `evidence/profile_authorisation/profile_ownership_results.txt` | Pass |
| Profile authorisation | PA3 | A logged-in user can still access their own profile route. | `evidence/profile_authorisation/profile_ownership_results.txt` | Pass |
| Profile authorisation | PA4 | Logged-out users are still redirected from profile routes to `/login`. | `evidence/profile_authorisation/profile_ownership_results.txt` | Pass |
| Session secret configuration | SK1 | Baseline showed a hard-coded `dev-secret-key`. | `evidence/session_secret/baseline_hard_coded_secret.txt` | Observed |
| Session secret configuration | SK2 | The app can use `SECRET_KEY` from the environment. | `evidence/session_secret/session_secret_config_results.txt` | Pass |
| Session secret configuration | SK3 | The app still has a local fallback when `SECRET_KEY` is absent. | `evidence/session_secret/session_secret_config_results.txt` | Pass |
| Session secret configuration | SK4 | `.env` is ignored and `.env.example` documents the expected setting. | `evidence/session_secret/session_secret_config_results.txt`; `.env.example`; `.gitignore` | Pass |

## Evidence Scripts

The captured outputs were produced or supported by these scripts:

| Area | Script |
| ---- | ------ |
| Baseline review | `evidence/baseline_review/test_baseline_review.py` |
| Password hashing | `evidence/password_hashing/test_password_hashing.py` |
| Password recovery | `evidence/password_recovery/test_password_recovery.py` |
| Route protection | `evidence/route_protection/test_route_protection.py` |
| Profile authorisation | `evidence/profile_authorisation/test_profile_authorisation.py` |
| Session secret configuration | `evidence/session_secret/test_session_secret_config.py` |

## Limitations

- Existing teaching-team seed accounts may still have plaintext entries in the ignored local `data/passwords.txt` file unless separately migrated. New signups are stored as hashes.
- The password recovery flow is a learning-app reset-request prototype. A production system should use secure single-use reset tokens, expiry, and a trusted delivery channel such as verified email.
- The app does not yet include CSRF protection for forms.
- The app does not include rate limiting, account lockout, or brute-force login protection.
- The profile ownership check protects user profile editing, but the app does not implement full role-based access control.
- The fallback `dev-secret-key` is suitable only for local development. A deployed environment should set a strong `SECRET_KEY`.

## Overall Assessment

The final tests show that the application now demonstrates the main learning goals: password hashing, hash-based login verification, no-disclosure password recovery behaviour, login-required route protection, profile ownership authorisation, and environment-based session-secret configuration.
