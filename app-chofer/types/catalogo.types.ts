export interface Prestadora {
  id: string;
  nombre: string;
  codigo_pais: string;
}

export interface Ciudad {
  id: string;
  nombre: string;
  codigo_postal: string | null;
  tenant_id: string;
  tenant_nombre: string;
}