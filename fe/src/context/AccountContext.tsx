/**
 * AccountContext.tsx
 * Qué: sesión de la cuenta de la base nueva (la que reserva, paga y administra el parqueadero).
 * Para qué: que el modal de reserva y el panel del dueño compartan la sesión sin pasar props.
 * Impacto: es independiente de AuthContext (módulos anteriores): usa otra clave en localStorage
 *          y otro token. Mientras ambos convivan, el usuario puede tener dos sesiones.
 */
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import * as accountsApi from "../api/accounts";
import type { Account, RegisterAccountPayload } from "../api/types";

const STORAGE_KEY = "dash_parking_account_token";

interface AccountContextValue {
  account: Account | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<Account>;
  register: (payload: RegisterAccountPayload) => Promise<Account>;
  logout: () => void;
}

const AccountContext = createContext<AccountContextValue | undefined>(undefined);

export function AccountProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [account, setAccount] = useState<Account | null>(null);
  const [loading, setLoading] = useState(token !== null);

  function saveToken(value: string | null) {
    if (value) localStorage.setItem(STORAGE_KEY, value);
    else localStorage.removeItem(STORAGE_KEY);
    setTokenState(value);
  }

  // Al abrir la app se valida el token guardado; si expiró, se limpia la sesión.
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    accountsApi
      .getMyAccount(token)
      .then(setAccount)
      .catch(() => {
        saveToken(null);
        setAccount(null);
      })
      .finally(() => setLoading(false));
    // Solo al montar: los cambios posteriores de token los maneja login/register/logout.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(email: string, password: string): Promise<Account> {
    const response = await accountsApi.loginAccount(email, password);
    saveToken(response.access_token);
    setAccount(response.user);
    return response.user;
  }

  async function register(payload: RegisterAccountPayload): Promise<Account> {
    const response = await accountsApi.registerAccount(payload);
    saveToken(response.access_token);
    setAccount(response.user);
    return response.user;
  }

  function logout(): void {
    saveToken(null);
    setAccount(null);
  }

  return (
    <AccountContext.Provider value={{ account, token, loading, login, register, logout }}>
      {children}
    </AccountContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAccount(): AccountContextValue {
  const context = useContext(AccountContext);
  if (!context) throw new Error("useAccount debe usarse dentro de un <AccountProvider>");
  return context;
}
