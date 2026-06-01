# 03 Password Recovery No-Disclosure

## Metadata

**Environment**: Local controlled deployment of the provided Flask codebase.  
**Purpose**: To replace password recovery behaviour that exposes stored credentials with a no-disclosure reset-request flow.

## Learning Note

**Concept learned**: Password recovery should not reveal an existing password or password hash. Since stored passwords are now hashes, the application cannot and should not retrieve the original password. A safer pattern is to record a reset request and return a generic message.

**Resources used**:

- OWASP Forgot Password Cheat Sheet: used to understand why forgot-password flows should use reset requests, consistent responses, and no credential disclosure.
- OWASP Authentication Cheat Sheet: used as supporting guidance that authentication features should avoid leaking sensitive credential information.
- Flask testing documentation: used to understand Flask's test client, which can send GET and POST requests to routes such as `/forgot` without manually opening the browser each time.

What I understood after reviewing the resources:

- A forgot-password feature should be a reset process, not a password retrieval process.
- The response should avoid revealing sensitive credential data.
- A simple learning-app version can record a reset request without implementing full email/token delivery.
- A production version would normally use a secure, single-use, expiring token delivered through a trusted side channel.

## Baseline Observation

The original `/forgot` route exposes the password storage file:

```python
@app.route('/forgot')
def forgot():
    if PASSWORDS_FILE.exists():
        return send_file(PASSWORDS_FILE, mimetype='text/plain')
    return Response('No passwords file found', mimetype='text/plain')
```

This is unsafe because it discloses stored credentials. Before password hashing, it revealed plaintext passwords. After password hashing, it would still reveal password hashes, which should also remain private.

## Planned Code Change

This step will only change password recovery behaviour:

1. Replace direct password-file download with a reset-request form.
2. On form submission, record the reset request in `data/password_reset_requests.jsonl`.
3. Return a generic no-disclosure message.
4. Avoid revealing the current password, password hash, or whether the submitted username exists.

## Test Plan

| ID | Test | Expected result |
| -- | ---- | --------------- |
| PR1 | Visit `/forgot` before the change. | Baseline shows password file disclosure. |
| PR2 | Visit `/forgot` after the change. | A reset-request form is shown instead of the password file. |
| PR3 | Submit an existing username. | A generic no-disclosure message is shown. |
| PR4 | Submit a non-existing username. | The same generic no-disclosure message is shown. |
| PR5 | Inspect reset request storage. | The request is recorded without exposing passwords or hashes in the response. |

## Baseline Test Evidence

Before changing the `/forgot` route, I tested the existing behaviour with the Flask test client.

For this evidence, the Flask test client was useful because it allowed me to inspect the HTTP status code and response body directly. This made it easy to check whether the response accidentally included credential data.

```text
PR1 baseline_forgot_status: 200
PR1 baseline_discloses_credential_data: True
PR1 baseline_response_preview:
tjones01:tjones01123
mscott01:mscott01123
hmitchell01:hmitchell01123
```

This confirms that the baseline recovery behaviour exposes credential data directly. It also shows why password recovery needs a separate fix even after password hashing: a recovery route should not expose the credential store at all.

## Test Evidence After Change

After replacing password-file download with a reset-request flow, I tested the route again with the Flask test client.

```text
PR2 forgot_get_status: 200
PR2 forgot_get_has_form: True
PR2 forgot_get_discloses_credentials: False
PR3 existing_user_status: 200
PR3 existing_user_generic_message: True
PR3 existing_user_discloses_credentials: False
PR4 fake_user_status: 200
PR4 fake_user_same_generic_message: True
PR4 fake_user_discloses_credentials: False
PR5 request_log_entries: 2
PR5 request_log_preview:
{"username": "tjones01", "requested_at": "18:45 -01/06/2026"}
{"username": "doesnotexist01", "requested_at": "18:45 -01/06/2026"}
```

These results show that `/forgot` now displays a reset-request form, returns the same generic message for an existing and non-existing username, and does not expose passwords or password hashes in the HTTP response.

## Reflection

This step helped me understand that password recovery is a separate security problem from password storage. After implementing password hashing, the system no longer stores plaintext passwords, but the recovery route still needed to be fixed because exposing password hashes is also unsafe. A secure recovery feature should not reveal either the original password or the stored hash.

The most important idea I learned was that password recovery should be based on a reset process, not a retrieval process. In the original version, `/forgot` behaved as if the system could simply return the password file. That was unsafe before password hashing because it revealed plaintext passwords, and it would still be unsafe after password hashing because it would reveal password hashes. The revised version avoids this by showing a reset-request form and returning a generic response.

The tests were useful because they checked both security and information leakage. PR2 confirmed that the password file is no longer returned. PR3 and PR4 were especially important because they checked that existing and non-existing usernames receive the same generic message. This matters because a password recovery system should avoid revealing whether a particular account exists. PR5 confirmed that the system can still record a reset request without exposing credentials in the HTTP response.

One limitation of this implementation is that it is still a simplified learning-app version of password recovery. It records reset requests, but it does not implement a complete production-grade reset process with single-use tokens, expiry times, email delivery, rate limiting, or audit controls. However, for this learning cycle, the main goal was to remove credential disclosure and understand the no-disclosure pattern used in safer recovery flows.