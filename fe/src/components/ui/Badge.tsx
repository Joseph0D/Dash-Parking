/** Badge.tsx — etiqueta de estado (libre/ocupado/reservado, pagado/pendiente, etc.). */
import "./Badge.css";

type BadgeTone = "success" | "danger" | "warning" | "neutral" | "accent";

export function Badge({ tone, children }: { tone: BadgeTone; children: React.ReactNode }) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}
