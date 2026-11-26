"""
R26 Fase 3b: Intervenciones, Checklist Respuestas y Ajustes de Modelo.

- Crea fleet.mantenimiento_intervencion (base para cierre manual en R26 y OT en R28).
- Crea fleet.mantenimiento_checklist_respuesta (base para R27).
- Agrega columna advertencias JSONB a fleet.mantenimiento_vencimiento.
- Agrega CHECK constraint a fleet.mantenimiento_plan_item (al menos un intervalo).
- Agrega columnas de sugerencias a fleet.mantenimiento_catalogo_componente.
- Elimina los umbrales de alerta de tenant.configuracion_mantenimiento (vuelven al plan).

Revision ID: m3_044
Revises: m3_043
Create Date: 2026-11-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'm3_044'
down_revision: Union[str, None] = 'm3_043'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Tabla: fleet.mantenimiento_intervencion
    # ---------------------------------------------------------
    op.execute("""
        CREATE TABLE fleet.mantenimiento_intervencion (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id UUID NOT NULL REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            vehiculo_id UUID NOT NULL REFERENCES fleet.vehiculo(id) ON DELETE CASCADE,
            plan_item_id UUID NOT NULL REFERENCES fleet.mantenimiento_plan_item(id) ON DELETE CASCADE,
            vencimiento_id UUID REFERENCES fleet.mantenimiento_vencimiento(id) ON DELETE SET NULL,
            
            km_real NUMERIC(12,2) NOT NULL,
            fecha_real DATE NOT NULL,
            
            costo NUMERIC(12,2),
            taller_nombre VARCHAR(150),
            observaciones TEXT,
            
            registrado_por UUID REFERENCES auth.usuario(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX idx_intervencion_vehiculo ON fleet.mantenimiento_intervencion(vehiculo_id);
        CREATE INDEX idx_intervencion_plan_item ON fleet.mantenimiento_intervencion(plan_item_id);
        CREATE INDEX idx_intervencion_control_base ON fleet.mantenimiento_intervencion(control_base_id);
    """)

    # ---------------------------------------------------------
    # 2. Tabla: fleet.mantenimiento_checklist_respuesta
    # ---------------------------------------------------------
    op.execute("""
        CREATE TABLE fleet.mantenimiento_checklist_respuesta (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            turno_id UUID NOT NULL REFERENCES fleet.turno_chofer(id) ON DELETE CASCADE,
            checklist_id UUID NOT NULL REFERENCES fleet.mantenimiento_checklist_inspeccion(id) ON DELETE CASCADE,
            
            respuesta VARCHAR(100) NOT NULL,
            severidad VARCHAR(20),
            observaciones TEXT,
            
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX idx_checklist_respuesta_turno ON fleet.mantenimiento_checklist_respuesta(turno_id);
    """)

    # ---------------------------------------------------------
    # 3. Alter: fleet.mantenimiento_vencimiento (advertencias)
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vencimiento 
        ADD COLUMN advertencias JSONB;
    """)

    # ---------------------------------------------------------
    # 4. Alter: fleet.mantenimiento_plan_item (CHECK constraint)
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE fleet.mantenimiento_plan_item 
        ADD CONSTRAINT ck_mantenimiento_plan_item_intervalo_requerido 
        CHECK (
            intervalo_km IS NOT NULL OR 
            intervalo_dias IS NOT NULL OR 
            intervalo_meses IS NOT NULL
        );
    """)

    # ---------------------------------------------------------
    # 5. Alter: fleet.mantenimiento_catalogo_componente (sugerencias)
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_componente 
        ADD COLUMN intervalo_km_sugerido INTEGER,
        ADD COLUMN intervalo_dias_sugerido INTEGER,
        ADD COLUMN intervalo_meses_sugerido INTEGER;
    """)

    # ---------------------------------------------------------
    # 6. Alter: tenant.configuracion_mantenimiento (DROP umbrales)
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE tenant.configuracion_mantenimiento 
        DROP COLUMN umbral_proximo_km,
        DROP COLUMN umbral_proximo_dias,
        DROP COLUMN umbral_critico_km,
        DROP COLUMN umbral_critico_dias;
    """)

def downgrade() -> None:
    # Revertir tenant.configuracion_mantenimiento
    op.execute("""
        ALTER TABLE tenant.configuracion_mantenimiento 
        ADD COLUMN umbral_proximo_km INTEGER NOT NULL DEFAULT 2000,
        ADD COLUMN umbral_proximo_dias INTEGER NOT NULL DEFAULT 30,
        ADD COLUMN umbral_critico_km INTEGER NOT NULL DEFAULT 500,
        ADD COLUMN umbral_critico_dias INTEGER NOT NULL DEFAULT 7;
    """)

    # Revertir catalogo_componente
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_componente 
        DROP COLUMN intervalo_km_sugerido,
        DROP COLUMN intervalo_dias_sugerido,
        DROP COLUMN intervalo_meses_sugerido;
    """)

    # Revertir plan_item
    op.execute("""
        ALTER TABLE fleet.mantenimiento_plan_item 
        DROP CONSTRAINT ck_mantenimiento_plan_item_intervalo_requerido;
    """)

    # Revertir vencimiento
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vencimiento 
        DROP COLUMN advertencias;
    """)

    # Borrar tablas nuevas
    op.execute("DROP TABLE IF EXISTS fleet.mantenimiento_checklist_respuesta;")
    op.execute("DROP TABLE IF EXISTS fleet.mantenimiento_intervencion;")