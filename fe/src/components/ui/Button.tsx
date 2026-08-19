/** Button.tsx — botón base del sistema, replica .btn-cta y variantes del mockup. */
import "./Button.css";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  loading?: boolean;
}

export function Button({ variant = "primary", loading = false, disabled, children, ...rest }: ButtonProps) {
  return (
    <button className={`btn btn--${variant}`} disabled={disabled || loading} {...rest}>
      {loading ? "Procesando..." : children}
    </button>
  );
}
