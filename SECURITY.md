# Security

Who Knows has no user accounts. The HTTP server is a local catalog plus a static page.

- Do not commit `.env`, proxy URLs, or tunnel tokens.
- `GET /api/refresh` triggers live store fetches and is unauthenticated. If you expose the board on the public internet, restrict that path at the reverse proxy.
- Store catalog endpoints are unofficial for PlayStation and Nintendo; treat responses as untrusted JSON.
- This project does not distribute games or circumvent store DRM.
