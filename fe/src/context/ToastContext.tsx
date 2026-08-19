/** ToastContext.tsx — permite disparar notificaciones desde cualquier página con useToast(). */
import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { ToastStack, type ToastMessage } from "../components/ui/Toast";

interface ToastContextValue {
  success: (text: string) => void;
  error: (text: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const push = useCallback((tone: ToastMessage["tone"], text: string) => {
    setToasts((prev) => [...prev, { id: Date.now() + Math.random(), tone, text }]);
  }, []);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const value: ToastContextValue = {
    success: (text) => push("success", text),
    error: (text) => push("error", text),
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastStack toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast debe usarse dentro de un <ToastProvider>");
  return context;
}
