# 04 Login-Required Route Protection

## Metadata

**Environment**: Local controlled deployment of the provided Flask codebase.  
**Purpose**: To require authentication before users can access private or user-specific routes.

## Learning Note

**Concept learned**: Password handling protects stored credentials, but private pages also need route-level authentication checks. A route should not rely only on hidden navigation links or template messages. If a route handles private or user-specific functionality, it should check whether the user is logged in before returning the page or processing the request.

**Resources used**:

- Flask sessions documentation: used to understand how this app stores authenticated state in `session["username"]`.
- Flask view decorators documentation: used to understand how a reusable decorator can wrap routes and enforce a shared check.
- Flask-Login documentation: used as a design reference for the common `@login_required` pattern, even though this learning app uses a small custom decorator.
- OWASP Authentication Cheat Sheet: used to connect route protection with the principle that protected functionality should require authentication.
- Flask testing documentation: used to test logged-out and logged-in route behaviour with Flask's test client.

What I understood after reviewing the resources:

- In this app, `session["username"]` is the current marker that a user is authenticated.
- Login-required behaviour should be enforced on the server side, not only through what links the interface shows.
- A reusable decorator is better than repeating the same `if not session.get("username")` check in every route.
- This step is about authentication only. Ownership and authorisation checks, such as whether one user may edit another user's profile, should be handled in a later focused cycle.

## Baseline Observation

The application already checks login for some routes, such as `/inbox`, but other private or user-specific pages are still reachable while logged out. For example, `/profile` renders a page asking the user to log in, and `/profiles` exposes the profile list route without requiring an authenticated session.

## Baseline Test Evidence

Before adding route protection, I tested several private or user-specific routes while logged out using Flask's test client.

```text
/profile: status=200, location=none
/profiles: status=200, location=none
/profiles/search?query=tjones01: status=200, location=none
/bookings: status=200, location=none
/bookings/new: status=200, location=none
/inbox: status=302, location=/login
/availability: status=200, location=none
public /: status=200
public /login: status=200
public /signup: status=200
public /forgot: status=200
```

This baseline shows inconsistent protection. `/inbox` already redirects logged-out users to `/login`, but several other private routes return HTTP 200 while logged out.

## Planned Code Change

This step will only add login-required route protection:

1. Add a small `login_required` decorator that checks `session.get("username")`.
2. Redirect logged-out users to `/login`.
3. Apply the decorator to private or user-specific routes.
4. Keep public routes such as `/`, `/login`, `/signup`, `/forgot`, and `/logout` available without login.
5. Leave profile ownership authorisation for the next learning cycle.

## Test Plan

| ID | Test | Expected result |
| -- | ---- | --------------- |
| RP1 | Visit protected routes while logged out. | The response redirects to `/login`. |
| RP2 | Visit public routes while logged out. | The route still returns normally. |
| RP3 | Log in and visit protected routes. | The route is accessible after authentication. |
| RP4 | Log out and revisit a protected route. | The route redirects to `/login` again. |

## Reflection Placeholder

Reflection will be completed after implementation and testing.
