/**
 * OAuth callback page that exchanges the GitHub authorization code for a session.
 *
 * This page is loaded after GitHub redirects back with a code and state
 * parameter. It exchanges the code for a JWT, stores the session, and
 * redirects to the home page.
 *
 * @module pages/AuthCallbackPage
 */

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { exchangeOAuthCode } from "@/api/auth";

/** Handles the GitHub OAuth callback and establishes the user session. */
export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setSession } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");

    if (!code || !state) {
      setError("Missing authorization parameters.");
      return;
    }

    exchangeOAuthCode(code, state)
      .then((response) => {
        setSession(response.access_token, response.user);
        navigate("/", { replace: true });
      })
      .catch((err) => {
        setError(err.message ?? "Authentication failed.");
      });
  }, [searchParams, navigate, setSession]);

  if (error) {
    return (
      <div>
        <h1>Authentication Failed</h1>
        <p>{error}</p>
        <a href="/">Return home</a>
      </div>
    );
  }

  return <p>Signing in...</p>;
}
