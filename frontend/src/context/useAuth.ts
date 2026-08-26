// src/context/useAuth.ts
import { createContext, useContext } from "react";
import type { User } from "../types";

export interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

// Export the raw context object so the Provider can use it
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Export the hook for your UI components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
