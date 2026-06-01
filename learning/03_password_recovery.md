# 03 Password Recovery No-Disclosure

## Metadata

**Environment**: Local controlled deployment of the provided Flask codebase.  
**Purpose**: To replace password recovery behaviour that exposes stored credentials with a no-disclosure reset-request flow.

## Learning Note

**Concept learned**: Password recovery should not reveal an existing password or password hash. Since stored passwords are now hashes, the application cannot and should not retrieve the original password. A safer pattern is to record a reset request and return a generic message.

**Resources used**:

- OWASP Forgot Password Cheat Sheet: used to understand why forgot-password flows should use reset requests, consistent responses, and no credential disclosure.
- OWASP Authentication Cheat Sheet: used as supporting guidance that authentication features should avoid leaking sensitive credential information.

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

## Reflection Placeholder

Reflection will be completed after implementation and testing.
