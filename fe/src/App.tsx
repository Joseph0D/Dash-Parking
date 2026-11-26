/** App.tsx — enrutador principal de Dash Parking. */
import { Navigate, Route, Routes } from "react-router-dom";
import { Navbar } from "./components/layout/Navbar";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { RolePanelLayout } from "./components/layout/RolePanelLayout";
import { LandingPage } from "./pages/LandingPage";
import { AvailabilityPage } from "./pages/AvailabilityPage";
import { OwnerPage } from "./pages/OwnerPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { ClientDashboard } from "./pages/client/ClientDashboard";
import { AdminDashboard } from "./pages/admin/AdminDashboard";
import { OwnerDashboard } from "./pages/owner/OwnerDashboard";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/ingreso" element={<LoginPage />} />
        <Route path="/cliente/*" element={<Navigate to="/cuenta" replace />} />
        <Route path="/usuario/*" element={<Navigate to="/admin" replace />} />
        {/* La página anterior de espacios (base vieja) se reemplazó por la reserva por franja */}
        <Route path="/espacios" element={<Navigate to="/disponibilidad" replace />} />
        <Route path="/disponibilidad" element={<AvailabilityPage />} />
        <Route path="/dueno" element={<OwnerPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegisterPage />} />
        <Route path="/recuperar-contrasena" element={<ForgotPasswordPage />} />
        <Route path="/restablecer-contrasena" element={<ResetPasswordPage />} />
        <Route
          path="/cuenta"
          element={
            <ProtectedRoute allowedRoles={["client"]}>
              <RolePanelLayout
                title="Cliente"
                defaultTab="session"
                links={[
                  { label: "Sesión y pagos", to: "/cuenta?tab=session", tab: "session" },
                  { label: "Mis vehículos y QR", to: "/cuenta?tab=vehicles", tab: "vehicles" },
                  { label: "Mis reservas", to: "/cuenta?tab=reservations", tab: "reservations" },
                ]}
              />
            </ProtectedRoute>
          }
        >
          <Route index element={<ClientDashboard />} />
        </Route>
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin", "operator"]}>
              <RolePanelLayout
                title="Administración"
                defaultTab="occupancy"
                links={[
                  { label: "Resumen de ocupación", to: "/admin?tab=occupancy", tab: "occupancy" },
                  { label: "Ingresos y salidas", to: "/admin?tab=entry-exit", tab: "entry-exit" },
                  { label: "Validar QR", to: "/admin?tab=qr", tab: "qr" },
                  { label: "Tarifas", to: "/admin?tab=rates", tab: "rates" },
                  { label: "Reportes", to: "/admin?tab=dashboard", tab: "dashboard" },
                ]}
              />
            </ProtectedRoute>
          }
        >
          <Route index element={<AdminDashboard />} />
        </Route>
        <Route
          path="/owner"
          element={
            <ProtectedRoute allowedRoles={["owner"]}>
              <RolePanelLayout
                title="Dueño"
                links={[
                  { label: "Mis parqueaderos", to: "/owner" },
                  { label: "Crear parqueadero", to: "/owner?crear=1", create: true },
                ]}
              />
            </ProtectedRoute>
          }
        >
          <Route index element={<OwnerDashboard />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
