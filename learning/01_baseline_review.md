# 01 Baseline Review

## Metadata

**Environment**: Local controlled deployment of the provided Flask codebase using the Flask test client.  
**Purpose**: To record the original authentication, password-handling, and authorisation behaviour before making security improvements.

## Learning Note

**Concept learned**: Before changing authentication or authorisation code, a secure development process should first identify the current behaviour and record why it is weak. This provides a clear before/after comparison for later implementation and testing.

**Resources referred to**:

-   OWASP Password Storage Cheat Sheet: used to understand why stored passwords should not be directly readable.
    
-   OWASP Authentication Cheat Sheet: used to identify authentication behaviours that should avoid credential disclosure.
    
-   OWASP Access Control Cheat Sheet: used to distinguish login/authentication from permission/authorisation checks.
    
-   Flask documentation on sessions: used to connect the app's `session["username"]` behaviour with authenticated state.
    

After reviewing these resources, I understood that authentication security is not one isolated change. It includes password storage, login verification, recovery behaviour, route protection, and authorisation decisions. A system can appear to have a working login feature while still being insecure if passwords are exposed, sessions are weakly managed, or authenticated users can access resources they do not own.

## Baseline Observation

The provided Flask application has several weaknesses relevant to my learning topic:

| ID | Weakness | Location | How it can be demonstrated |
| -- | -------- | -------- | -------------------------- |
| B1 | Passwords are stored in plaintext. | `data/passwords.txt` and `set_pwd()` in `app.py`. | The password file contains entries such as `tjones01:tjones01123`, where the stored value is directly readable. |
| B2 | Login compares the submitted password directly with the stored credential value. | `/login` route in `app.py`. | Code review shows that the submitted password is compared with the stored value, and a baseline login test confirms that the plaintext login path succeeds. | 
| B3 | Password recovery discloses credentials. | `/forgot` route in `app.py`. | Visiting `/forgot` directly returns the password file instead of using a reset-based recovery process. |
| B4 | Some routes related to private or user-specific functionality do not consistently enforce login. | `/profile`, `/profiles`, and related routes. | Logged-out requests return page content or route responses instead of consistently redirecting or denying access. | 
| B5 | A logged-in user can access another user's profile edit route. | `/profile/<username>` in `app.py`. | After logging in as one user, requesting another user's profile route returns HTTP 200, showing that the route is reachable without an ownership check. |
| B6 | The session secret is hard-coded. | `app.secret_key = 'dev-secret-key'` in `app.py`. | The secret is fixed in source code rather than coming from configuration or an environment variable. |

## Baseline Test Evidence

These results were produced using a Flask test client in a local controlled deployment of the provided codebase. The tests used dummy accounts only and did not interact with real user data.

```text
plaintext_password_file: OBSERVED
forgot_discloses_password_file: OBSERVED
profile_logged_out_not_redirected: OBSERVED
profiles_logged_out_accessible: OBSERVED
plaintext_login_succeeds: OBSERVED
cross_user_profile_route_accessible: OBSERVED
forgot_status: 200
profile_logged_out_status: 200
profiles_logged_out_status: 200
other_profile_status: 200
```

The baseline output shows that the application has several behaviours worth improving. In particular, the password file is directly readable in the local deployment, the password recovery route exposes that file, plaintext login succeeds, and the profile route for another user is reachable.

## Limitations of this Baseline Review

These checks show the baseline behaviour of the provided codebase in a controlled local environment. They do not prove that the cloud deployment has exactly the same filesystem state or configuration. However, they are suitable for this self-learning task because the goal is to learn secure Flask authentication by modifying and assessing the provided application code.

Some results also need to be interpreted carefully. For example, a `200` response does not always prove that private data was exposed. It shows that the route was reachable and therefore needs closer inspection. The important security question is whether the route reveals private data, permits an unauthorised action, or requires authentication instead.

## Reflection

The most useful part of this step was seeing that the weaknesses are connected. Plaintext storage makes password disclosure more serious, password recovery exposes the same file, and login relies on direct comparison because there is no password hashing. I also noticed that authentication and authorisation are separate: even if login works, `/profile/<username>` still needs to check whether the logged-in user owns the profile being edited.

This baseline review also changed my planned work order. I originally thought route protection would be the first change, but the evidence showed that password hashing should come first because the login and recovery weaknesses both depend on plaintext credential storage. Therefore, I will prioritise password hashing because it lays the foundation for safer login verification.