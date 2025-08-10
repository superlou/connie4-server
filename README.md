1. Ember client: Click LogInOut component
2. Ember client: LogInOut component fetches Google login URL from backend
3. FastAPI backend: Sends Google login URL
4. Ember client: window.location.assign to Google login URL
5. Google auth: Does login and provides auth token to Ember client Auth route
6. Ember client: Auth route fetches FastAPI backend /auth/google endpoint with Google authorization code
7. FastAPI backend: Uses code to get Google token
8. FastAPI backend: Uses Google token to get Google user info
9. FastAPI backend: Creates Backend JWT with user ID (email)
10. FastAPI backend: Stores Google JWT and Backend JWT, associated by email
11. FastAPI backend: Responds to client with Backend JWT
12. Ember client: Calls ember-simple-auth custom Authenticator with Backend JWT
13. Ember client: Custom Authenticator persists the Backend JWT
14. Ember client: If everything works so far, transition to /users/me
15. Ember client: Ember data for user model fetches FastAPI backend /current_user, including stored Backend JWT in the header as a bearer token
16. ... from here on, Ember model fetches just need to always use the ember-simple-auth session JWT? 
