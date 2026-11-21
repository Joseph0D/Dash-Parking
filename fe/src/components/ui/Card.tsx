/** Card.tsx — contenedor blanco con sombra suave, unidad visual base del mockup. */
import "./Card.css";

export function Card({
  children,
  className = "",
  style,
}: {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  return <div className={`card ${className}`} style={style}>{children}</div>;
}
