import React from "react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { setAuthToken } from "../lib/api";

type AuthCtx = {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthCtx>({} as AuthCtx);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const navigate = useNavigate();

  useEffect(() => {
    setAuthToken(token || undefined);
  }, [token]);

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);
    const { data } = await api.post("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
    navigate("/dashboard", { replace: true });
  };

  const signup = async (email: string, password: string) => {
    await api.post("/auth/signup", { email, password });
    navigate("/login", { replace: true });
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    navigate("/login", { replace: true });
  };

  const value = useMemo(() => ({ token, login, signup, logout }), [token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
