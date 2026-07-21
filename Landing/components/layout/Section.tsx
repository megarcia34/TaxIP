import { ReactNode } from "react";

type SectionProps = {
  children: ReactNode;
  background?: "white" | "gray" | "yellow" | "dark" | "primary";
  padding?: "default" | "none";
  className?: string;
};

export function Section({ 
  children, 
  background = "white", 
  padding = "default", 
  className = "" 
}: SectionProps) {
  
  const bgClasses: Record<string, string> = {
    white: "section-white",
    gray: "section-gray",
    yellow: "section-yellow",
    dark: "section-dark",
    primary: "section", // Usamos 'section' base y el color se puede manejar con className o inline
  };

  const paddingClass = padding === "none" ? "" : "section";
  const bgClass = bgClasses[background] || "section-white";
  
  // Combinamos las clases, asegurando que no haya duplicados de "section"
  const finalClass = `${paddingClass} ${bgClass} ${className}`.replace(/\s+/g, ' ').trim();

  return <section className={finalClass}>{children}</section>;
}