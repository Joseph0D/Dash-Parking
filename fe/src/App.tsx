/** App.tsx — enrutador principal de Dash Parking. */
import { Navigate, Route, Routes } from "react-router-dom";
import { Navbar } from "./components/layout/Navbar";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { LandingPage } from "./pages/LandingPage";
import { AvailabilityPage } from "./pages/AvailabilityPage";
import { OwnerPage } from "./pages/OwnerPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ClientDashboard } from "./pages/client/ClientDashboard";
import { AdminDashboard } from "./pages/admin/AdminDashboard";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        {/* La página anterior de espacios (base vieja) se reemplazó por la reserva por franja */}
        <Route path="/espacios" element={<Navigate to="/disponibilidad" replace />} />
        <Route path="/disponibilidad" element={<AvailabilityPage />} />
        <Route path="/dueno" element={<OwnerPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegisterPage />} />
        <Route
          path="/cuenta"
          element={
            <ProtectedRoute allowedRoles={["client"]}>
              <ClientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin", "operator"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
