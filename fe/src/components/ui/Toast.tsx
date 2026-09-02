/**
 * Toast.tsx
 * Qué: notificación efímera de éxito/error, para dar retroalimentación inmediata (RNF-003.3).
 * Para qué: reemplazar los alert()/confirm() del mockup original, que bloquean el hilo del
 *           navegador y no son accesibles.
 */
import { useEffect } from "react";
import "./Toast.css";

export interface ToastMessage {
  id: number;
  tone: "success" | "error";
  text: string;
}

export function ToastStack({ toasts, onDismiss }: { toasts: ToastMessage[]; onDismiss: (id: number) => void }) {
  return (
    <div className="toast-stack" role="status" aria-live="polite">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onDismiss }: { toast: ToastMessage; onDismiss: (id: number) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), 4000);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  return (
    <div className={`toast toast--${toast.tone}`}>
      {toast.text}
      <button className="toast__close" onClick={() => onDismiss(toast.id)} aria-label="Cerrar notificación">
        ×
      </button>
    </div>
  );
}
