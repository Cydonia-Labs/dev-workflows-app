/**
 * API functions for authentication.
 *
 * @module api/auth
 */

import { apiFetch } from "./client";
import type { TokenResponse, UserResponse } from "@/types/auth";

/**
 * Exchange a GitHub OAuth callback code for a session token.
 *
 * @param code - Authorization code from GitHub.
 * @param state - CSRF state parameter.
 * @returns The session token and user profile.
 */
export function exchangeOAuthCode(code: string, state: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>(`/api/auth/github/callback?code=${code}&state=${state}`);
}

/**
 * Fetch the currently authenticated user's profile.
 *
 * @returns The user's profile.
 * @throws Error if not authenticated.
 */
export function fetchCurrentUser(): Promise<UserResponse> {
  return apiFetch<UserResponse>("/api/auth/me");
}
