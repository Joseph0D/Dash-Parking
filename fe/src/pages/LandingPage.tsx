import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { UserRole } from "../api/types";
import { ParkingMap } from "../components/ParkingMap";
import "./LandingPage.css";

const RESERVATION_STEPS = [
  {
    title: "Elige parqueadero y horario",
    description: "Consulta ubicaciones y disponibilidad real para las horas de tu visita.",
  },
  {
    title: "Registra tu vehículo",
    description: "Crea tu cuenta de cliente y agrega la placa o el tipo de vehículo.",
  },
  {
    title: "Confirma tu reserva",
    description: "Selecciona un espacio disponible y confirma. El sistema valida el cupo al guardar.",
  },
];

const FEATURES = [
  {
    title: "Disponibilidad por horario",
    description: "Consulta espacios libres, ocupados y reservados para el horario que necesitas.",
  },
  {
    title: "Gestión para propietarios",
    description: "Registra tu parqueadero, ubicación, horarios, espacios y tarifas por categoría.",
  },
  {
    title: "Administración conectada",
    description: "El equipo autorizado gestiona ocupación, tarifas, sesiones y reportes.",
  },
];

function panelPath(role: UserRole): string {
  if (role === "owner") return "/owner";
  if (role === "admin" || role === "operator") return "/admin";
  return "/cuenta";
}

export function LandingPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <main className="home-page">
      <div className="contenedor">
        <section className="hero">
          <div className="hero__copy">
            <p className="home-eyebrow">Estacionamiento más sencillo</p>
            <h1>Tu espacio ya está esperando.</h1>
            <p className="hero__texto">
              Consulta parqueaderos, revisa disponibilidad por horario y reserva desde un solo lugar.
            </p>
            <div className="hero__acciones">
              <Link className="btn btn--primary" to="/disponibilidad">Ver disponibilidad</Link>
              {user ? (
                <button className="btn btn--ghost" onClick={() => navigate(panelPath(user.role))}>
                  Ir a mi panel
                </button>
              ) : (
                <Link className="btn btn--ghost" to="/registro">Crear cuenta</Link>
              )}
            </div>
          </div>
          <div className="hero__plano" aria-hidden="true">
            <div className="home-parking-illustration">
              <div className="home-parking-illustration__street">
                <span className="home-parking-illustration__lane" />
                <span className="home-parking-illustration__car"><i /></span>
              </div>
              <div className="home-parking-illustration__caption">
                <strong>Dash Parking</strong>
                <span>Ubicaciones y reservas en un solo lugar</span>
              </div>
            </div>
          </div>
        </section>

        <section className="seccion" id="parqueaderos">
          <div className="seccion__cab">
            <h2>Parqueaderos y disponibilidad</h2>
            <p>Consulta las ubicaciones publicadas y revisa sus cupos para el horario que necesitas.</p>
          </div>
          <div id="mapa"><ParkingMap /></div>
        </section>

        <section className="seccion" id="reservas">
          <div className="seccion__cab">
            <h2>Reserva en tres pasos</h2>
            <p>Explora sin cuenta. Para confirmar una reserva, inicia sesión como cliente.</p>
          </div>
          <ol className="pasos">
            {RESERVATION_STEPS.map((step) => (
              <li key={step.title}>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </li>
            ))}
          </ol>
          <Link className="btn btn--primary" to="/disponibilidad">Reservar ahora</Link>
        </section>

        <section className="seccion" id="servicios">
          <div className="seccion__cab">
            <h2>Una plataforma para cada rol</h2>
            <p>El acceso a cada panel y sus operaciones está controlado por la cuenta autenticada.</p>
          </div>
          <div className="rasgos">
            {FEATURES.map((feature) => (
              <article className="rasgo" key={feature.title}>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="seccion" id="nosotros">
          <div className="seccion__cab">
            <h2>Estacionar con más claridad</h2>
            <p>Dash Parking reúne en un solo flujo la consulta, reserva y administración de parqueaderos.</p>
          </div>
          <div className="home-about">
            <article>
              <h3>Para conductores</h3>
              <p>Consulta espacios antes de llegar, registra vehículos y organiza tus reservas desde tu cuenta.</p>
            </article>
            <article>
              <h3>Para propietarios</h3>
              <p>Publica parqueaderos con ubicación, horario, capacidad y tarifas administradas desde el panel.</p>
            </article>
          </div>
        </section>

        <section className="seccion home-manual" id="manual">
          <div className="seccion__cab">
            <h2>Guía rápida</h2>
            <p>Flujo de inicio a fin para cada tipo de cuenta.</p>
          </div>
          <details>
            <summary>Cliente: registrarse y reservar</summary>
            <div><ol>
              <li>En Crear cuenta, selecciona Cliente y completa tus datos.</li>
              <li>Registra un vehículo desde Mi cuenta.</li>
              <li>En Disponibilidad elige parqueadero, tipo de vehículo y horario.</li>
              <li>Escoge un espacio libre, selecciona tu vehículo y confirma la reserva.</li>
              <li>Consulta o cancela reservas desde el panel, según el estado permitido.</li>
            </ol></div>
          </details>
          <details>
            <summary>Dueño: publicar un parqueadero</summary>
            <div><ol>
              <li>En Crear cuenta, selecciona Dueño de parqueadero.</li>
              <li>Desde Mis parqueaderos, pulsa Crear parqueadero.</li>
              <li>Completa identificación y dirección; confirma el punto en el mapa.</li>
              <li>Configura horarios y define cantidad de espacios y tarifa para cada categoría.</li>
              <li>Guarda para que los clientes puedan consultar y reservar tus espacios.</li>
            </ol></div>
          </details>
          <details>
            <summary>Administrador y operador</summary>
            <div><p>Inicia sesión con una cuenta autorizada para consultar ocupación, registrar ingresos y salidas, administrar tarifas y revisar reportes.</p></div>
          </details>
        </section>

        <footer className="home-footer">
          <span className="brand">Dash<span>Parking</span></span>
          <nav aria-label="Enlaces del pie de página">
            <a href="#parqueaderos">Parqueaderos</a>
            <a href="#reservas">Reservas</a>
            <a href="#manual">Guía rápida</a>
            <Link to="/registro?tipo=dueno">Publica tu parqueadero</Link>
          </nav>
          <small>Gestiona tus cuentas y operaciones desde tu panel de Dash Parking.</small>
        </footer>
      </div>
    </main>
  );
}
