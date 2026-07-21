import * as React from "react";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "outline" | "secondary";
  size?: "default" | "sm" | "lg";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "primary", size = "default", children, ...props }, ref) => {
    const variants = {
      primary: "btn btn-primary",
      outline: "btn btn-outline",
      secondary: "btn btn-secondary",
    };
    
    const sizes = {
      default: "",
      sm: "btn-sm",
      lg: "btn-lg",
    };
    
    return (
      <button
        ref={ref}
        className={`${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";