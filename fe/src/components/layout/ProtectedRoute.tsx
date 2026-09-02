/**
 * ProtectedRoute.tsx
 * Qué: envuelve rutas que requieren sesión, y opcionalmente un rol específico.
 * Para qué: sustento de RNF-003.2 — el menú y las rutas solo muestran lo habilitado por rol
 *           (ej. un cliente nunca debería poder navegar directo a /admin escribiendo la URL).
 */
import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import type { UserRole } from "../../api/types";

export function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}) {
  const { user, loading } = useAuth();

  if (loading) return <div className="page-loading">Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
