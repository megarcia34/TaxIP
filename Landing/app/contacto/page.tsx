import { redirect } from "next/navigation";

export default function ContactoPage() {
  const whatsappNumber = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "5491123456789";
  const whatsappUrl = `https://wa.me/${whatsappNumber}`;
  
  redirect(whatsappUrl);
}