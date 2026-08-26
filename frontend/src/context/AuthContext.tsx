// src/context/AuthContext.tsx
import { useState, type ReactNode } from "react";
import { apiClient } from "../api/client";
import type { User, LoginResponse } from "../types";
import { AuthContext } from "./useAuth"; // Import the context from your hook file

export function AuthProvider({ children }: { children: ReactNode; }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem("hims_user");
    return stored ? JSON.parse(stored) : null;
  });
  const [isLoading, setIsLoading] = useState(false);

  async function login(username: string, password: string) {
    setIsLoading(true);
    try {
      const { data } = await apiClient.post<LoginResponse>("/auth/login/", { username, password });
      localStorage.setItem("hims_access_token", data.access);
      localStorage.setItem("hims_refresh_token", data.refresh);
      localStorage.setItem("hims_user", JSON.stringify(data.user));
      setUser(data.user);
    } finally {
      setIsLoading(false);
    }
  }

  function logout() {
    localStorage.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}
