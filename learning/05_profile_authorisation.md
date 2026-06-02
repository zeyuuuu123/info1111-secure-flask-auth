# 05 Profile Ownership Authorisation

## Metadata

**Environment**: Local controlled deployment of the provided Flask codebase.  
**Purpose**: To prevent one authenticated user from accessing or editing another user's profile route.

## Learning Note

**Concept learned**: Authentication and authorisation are different. Authentication checks whether the user is logged in. Authorisation checks whether that logged-in user is allowed to perform a specific action or access a specific resource.

**Resources used**:

- OWASP Access Control Cheat Sheet: used to understand why server-side permission checks are needed for user-specific resources.
- Flask sessions documentation: used to connect the logged-in identity to `session["username"]`.
- Flask `abort()` documentation: used to understand how the app can return HTTP `403 Forbidden` when a logged-in user is not authorised for a route.
- Flask testing documentation: used to test cross-user access with Flask's test client.

What I understood after reviewing the resources:

- Login-required route protection is not enough for user-specific pages.
- The server should check ownership before returning or modifying private profile data.
- Hiding a link in the interface is not an authorisation control because users can still request a URL directly.
- A `403 Forbidden` response is appropriate when the user is authenticated but not permitted to access the requested resource.

## Baseline Observation

The `/profile/<username>` route now requires login, but it does not yet check whether the requested profile username matches the logged-in username. This means a logged-in user may still request another user's profile route directly.

## Planned Code Change

This step will only add a profile ownership check:

1. Keep the existing `@login_required` protection.
2. In `/profile/<username>`, compare `session.get("username")` with the route's `username`.
3. If they do not match, return `403 Forbidden` using `abort(403)`.
4. Keep the user's own `/profile` and `/profile/<own_username>` routes accessible.

## Test Plan

| ID | Test | Expected result |
| -- | ---- | --------------- |
| PA1 | Log in as User A and request `/profile/UserB`. | Baseline shows the route is reachable before the fix. |
| PA2 | Log in as User A and request `/profile/UserB` after the fix. | Response is HTTP `403 Forbidden`. |
| PA3 | Log in as User A and request `/profile/UserA`. | Response is HTTP `200`. |
| PA4 | Request `/profile/UserA` while logged out. | Response redirects to `/login`. |

## Reflection Placeholder

Reflection will be completed after implementation and testing.
