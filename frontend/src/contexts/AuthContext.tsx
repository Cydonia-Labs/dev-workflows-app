/**
 * Authentication context for managing user session state.
 *
 * Provides the current user, login/logout functions, and
 * authentication status to all components via React Context.
 *
 * @module contexts/AuthContext
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { clearToken, getStoredToken, storeToken } from "@/api/client";
import { fetchCurrentUser } from "@/api/auth";
import type { UserResponse } from "@/types/auth";

/** Shape of the authentication context value. */
interface AuthContextValue {
  /** The currently authenticated user, or null if not logged in. */
  user: UserResponse | null;
  /** Whether the auth state is still being loaded on app startup. */
  loading: boolean;
  /** Whether the user is authenticated. */
  isAuthenticated: boolean;
  /** Redirect to GitHub OAuth login page. */
  login: () => void;
  /** Clear the session and log out. */
  logout: () => void;
  /** Store a token and user after OAuth callback. */
  setSession: (token: string, user: UserResponse) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/** Props for the {@link AuthProvider} component. */
interface AuthProviderProps {
  /** Child components that can access auth state. */
  children: ReactNode;
}

/**
 * Provides authentication state to the component tree.
 *
 * On mount, checks for a stored JWT and validates it by fetching
 * the user profile. If the token is invalid or expired, clears it.
 *
 * @example
 * ```tsx
 * <AuthProvider>
 *   <App />
 * </AuthProvider>
 * ```
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setLoading(false);
      return;
    }

    fetchCurrentUser()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  function login() {
    window.location.href = "/api/auth/github";
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  function setSession(token: string, newUser: UserResponse) {
    storeToken(token);
    setUser(newUser);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: user !== null,
        login,
        logout,
        setSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access the authentication context.
 *
 * @returns The current auth context value.
 * @throws Error if used outside of an AuthProvider.
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
