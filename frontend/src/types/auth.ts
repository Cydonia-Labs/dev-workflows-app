/** Public user profile returned by the API. */
export interface UserResponse {
  /** Unique user identifier. */
  id: string;
  /** GitHub username. */
  github_login: string;
  /** Display name from GitHub profile. */
  display_name: string;
  /** URL to GitHub avatar image. */
  avatar_url: string | null;
  /** Whether the user has admin privileges. */
  is_admin: boolean;
}

/** Response from the OAuth callback endpoint. */
export interface TokenResponse {
  /** JWT session token for subsequent API calls. */
  access_token: string;
  /** Always "bearer". */
  token_type: string;
  /** The authenticated user's profile. */
  user: UserResponse;
}
