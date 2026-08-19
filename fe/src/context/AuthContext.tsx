/**
 * AuthContext.tsx
 * Qué: estado global de sesión (usuario autenticado + token), disponible en toda la app.
 * Para qué: evitar pasar props de sesión manualmente por cada página (RF-012).
 * Impacto: si el token guardado ya expiró, `me()` falla y aquí se limpia la sesión —
 *          así ninguna pantalla queda mostrando datos de un usuario ya no autenticado.
 */
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import * as authApi from "../api/auth";
import { setToken } from "../api/client";
import type { User } from "../api/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authApi
      .me()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string): Promise<User> {
    const response = await authApi.login(email, password);
    setToken(response.access_token);
    setUser(response.user);
    return response.user;
  }

  async function register(name: string, email: string, password: string): Promise<User> {
    const response = await authApi.register(name, email, password);
    setToken(response.access_token);
    setUser(response.user);
    return response.user;
  }

  function logout(): void {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth debe usarse dentro de un <AuthProvider>");
  return context;
}
