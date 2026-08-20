

"""auto gestion y capacidades

Revision ID: 7c7fab20e3bb
Revises: 276dc5da658a
Create Date: 2026-08-06 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '7c7fab20e3bb'
down_revision = '276dc5da658a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # PARTE 1: MIGRAR DATOS ANTES DE TOCAR CONSTRAINTS
    # ============================================
    
    # 1.1 Migrar 'MENSUAL' -> 'SEMANAL' (el nuevo constraint no acepta MENSUAL)
    op.execute("""
        UPDATE fleet.contrato_vehiculo 
        SET modalidad_computo = 'SEMANAL' 
        WHERE modalidad_computo = 'MENSUAL'
    """)
    
    # 1.2 Migrar valores obsoletos de tratamiento_dia
    op.execute("""
        UPDATE fleet.contrato_vehiculo 
        SET tratamiento_dia_no_trabajado = 'POR_DISPONIBILIDAD' 
        WHERE tratamiento_dia_no_trabajado IN ('NO_COBRA', 'DESCUENTO_PROPORCIONAL')
    """)
    
    # 1.3 Forzar a NULL valores no válidos (para contratos AUTO_GESTION)
    op.execute("""
        UPDATE fleet.contrato_vehiculo 
        SET modalidad_computo = NULL 
        WHERE modalidad_computo IS NOT NULL 
          AND modalidad_computo NOT IN ('DIARIO', 'SEMANAL')
    """)
    
    op.execute("""
        UPDATE fleet.contrato_vehiculo 
        SET tratamiento_dia_no_trabajado = NULL 
        WHERE tratamiento_dia_no_trabajado IS NOT NULL 
          AND tratamiento_dia_no_trabajado NOT IN ('POR_DISPONIBILIDAD', 'POR_USO_EFECTIVO')
    """)
    
    # ============================================
    # PARTE 2: ELIMINAR CONSTRAINTS VIEJOS
    # ============================================
    
    # Los nombres reales de los constraints creados en la migración anterior
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS chk_contrato_modalidad_computo")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS chk_contrato_tratamiento_dia")
    
    # ============================================
    # PARTE 3: CREAR CONSTRAINTS NUEVOS (PERMITEN NULL para AUTO_GESTION)
    # ============================================
    
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo 
        ADD CONSTRAINT chk_modalidad_computo 
        CHECK (
            modalidad_computo IS NULL 
            OR modalidad_computo IN ('DIARIO', 'SEMANAL')
        )
    """)
    
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo 
        ADD CONSTRAINT chk_tratamiento_dia 
        CHECK (
            tratamiento_dia_no_trabajado IS NULL 
            OR tratamiento_dia_no_trabajado IN ('POR_DISPONIBILIDAD', 'POR_USO_EFECTIVO')
        )
    """)
    
    # ============================================
    # PARTE 4: CREAR TABLA auth.usuario_rol
    # ============================================
    
    op.create_table(
        'usuario_rol',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('usuario_id', UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_usuario_id', UUID(as_uuid=True), nullable=False),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('fecha_inicio', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id', 'tipo_usuario_id', name='uq_usuario_rol_unico'),
        sa.ForeignKeyConstraint(['usuario_id'], ['auth.usuario.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tipo_usuario_id'], ['auth.tipo_usuario.id'], ondelete='CASCADE'),
        schema='auth'
    )
    
    # Índices
    op.create_index('idx_usuario_rol_usuario', 'usuario_rol', ['usuario_id', 'activo'], schema='auth')
    op.create_index('idx_usuario_rol_tipo', 'usuario_rol', ['tipo_usuario_id', 'activo'], schema='auth')
    op.create_index('idx_usuario_rol_vigencia', 'usuario_rol', 
                    ['usuario_id', 'fecha_inicio', 'fecha_fin'], schema='auth')
    
    # Trigger de updated_at (aprovechamos la función existente)
    op.execute("""
        CREATE TRIGGER trigger_usuario_rol_updated_at
            BEFORE UPDATE ON auth.usuario_rol
            FOR EACH ROW
            EXECUTE FUNCTION actualizar_updated_at();
    """)
    
    # Comentario descriptivo
    op.execute("""
        COMMENT ON TABLE auth.usuario_rol IS 
        'Capacidades adicionales de una identidad de usuario (ej. propietario con capacidad conductor)'
    """)
    
    # ============================================
    # PARTE 5: VERIFICACIÓN DE CONSISTENCIA
    # ============================================
    
    op.execute("""
        DO $$
        DECLARE
            inconsistent_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO inconsistent_count
            FROM fleet.contrato_vehiculo
            WHERE tipo_contrato = 'AUTO_GESTION'
              AND (canon_diario IS NOT NULL 
                   OR km_incluidos_dia IS NOT NULL 
                   OR valor_km_excedente IS NOT NULL
                   OR porcentaje_chofer IS NOT NULL);
            
            IF inconsistent_count > 0 THEN
                RAISE WARNING 'Se encontraron % contratos AUTO_GESTION con parámetros económicos inconsistentes', inconsistent_count;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # ============================================
    # REVERTIR PARTE 4: Eliminar auth.usuario_rol
    # ============================================
    
    op.execute("DROP TRIGGER IF EXISTS trigger_usuario_rol_updated_at ON auth.usuario_rol")
    op.drop_index('idx_usuario_rol_vigencia', table_name='usuario_rol', schema='auth')
    op.drop_index('idx_usuario_rol_tipo', table_name='usuario_rol', schema='auth')
    op.drop_index('idx_usuario_rol_usuario', table_name='usuario_rol', schema='auth')
    op.drop_table('usuario_rol', schema='auth')
    
    # ============================================
    # REVERTIR PARTE 3: Restaurar constraints originales
    # ============================================
    
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS chk_tratamiento_dia")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS chk_modalidad_computo")
    
    # Restaurar los constraints originales (NO permitían NULL)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo 
        ADD CONSTRAINT chk_contrato_modalidad_computo 
        CHECK (modalidad_computo IN ('DIARIO', 'SEMANAL', 'MENSUAL'))
    """)
    
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo 
        ADD CONSTRAINT chk_contrato_tratamiento_dia 
        CHECK (tratamiento_dia_no_trabajado IN ('POR_DISPONIBILIDAD', 'NO_COBRA', 'DESCUENTO_PROPORCIONAL'))
    """)