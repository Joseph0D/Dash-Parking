import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Sprint 0: solo el esqueleto de la app monta correctamente.
// Las pantallas reales (ingreso, salida, ocupación) se construyen desde el Sprint 5
// (Semana 6 — Integración Frontend-Backend), según entregable-s01-plan-de-trabajo.md.
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
