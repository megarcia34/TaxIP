import Image from "next/image";
import Link from "next/link";

export function Logo() {
  return (
    <Link href="/" style={{ display: "flex", alignItems: "center", gap: "0.5rem", textDecoration: "none" }}>
      <div style={{ 
        display: "flex", 
        width: "2.5rem", 
        height: "2.5rem", 
        alignItems: "center", 
        justifyContent: "center", 
        borderRadius: "0.75rem", 
        backgroundColor: "#FBBF24" 
      }}>
        <Image 
          src="/logos/logo-small.png" 
          alt="TAXIP" 
          width={32} 
          height={32} 
          style={{ objectFit: "contain" }} 
        />
      </div>
      <span style={{ fontSize: "1.25rem", fontWeight: 700, color: "#1a1a1a" }}>TAXIP</span>
    </Link>
  );
}