"""Security headers middleware.

Adds standard security headers to all responses to prevent common
web attacks (clickjacking, MIME-sniffing, downgrade attacks).
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every HTTP response.

    Headers added:
    - X-Content-Type-Options: nosniff — prevents MIME-type sniffing
    - X-Frame-Options: DENY — prevents clickjacking via iframes
    - Strict-Transport-Security — enforces HTTPS for 1 year
    - Referrer-Policy: strict-origin-when-cross-origin — limits referrer leakage
    - X-XSS-Protection: 0 — disables browser XSS filter (modern CSP is preferred)
    - Permissions-Policy — restricts browser feature access
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers after the response is generated.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            The response with security headers added.
        """
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Disable legacy XSS filter — modern CSP is the correct defense
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        return response
