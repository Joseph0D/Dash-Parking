/** Card.tsx — contenedor blanco con sombra suave, unidad visual base del mockup. */
import "./Card.css";

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`card ${className}`}>{children}</div>;
}
