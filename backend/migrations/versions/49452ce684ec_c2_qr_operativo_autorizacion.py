

"""c2 qr operativo autorizacion

Revision ID: 49452ce684ec
Revises: 7c7fab20e3bb
Create Date: 2026-08-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '49452ce684ec'
down_revision = '7c7fab20e3bb'  # <-- Reemplazar con el ID de 'alembic current'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # PARTE 1: Tabla auth.autorizacion_inicio
    # ============================================================
    op.create_table(
        'autorizacion_inicio',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('contrato_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chofer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('control_base_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_contrato', sa.String(20), nullable=True),
        sa.Column('turno_contractual', sa.String(20), nullable=True),
        sa.Column('dia_contractual', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('qr_referencia', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', name='uq_autorizacion_inicio_token'),
        sa.ForeignKeyConstraint(['contrato_id'], ['fleet.contrato_vehiculo.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chofer_id'], ['auth.usuario.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['fleet.vehiculo.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['control_base_id'], ['tenant.control_base.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['auth.usuario.id'], ondelete='SET NULL'),
        schema='auth'
    )

    # Índices
    op.create_index('idx_autorizacion_inicio_token', 'autorizacion_inicio', 
                    ['token'], schema='auth')
    # Índice parcial: solo autorizaciones no usadas (las activas)
    op.create_index(
        'idx_autorizacion_inicio_expires',
        'autorizacion_inicio',
        ['expires_at'],
        schema='auth',
        postgresql_where=sa.text('used_at IS NULL')
    )
    op.create_index('idx_autorizacion_inicio_contrato', 'autorizacion_inicio',
                    ['contrato_id'], schema='auth')
    op.create_index('idx_autorizacion_inicio_chofer', 'autorizacion_inicio',
                    ['chofer_id'], schema='auth')

    # Comentarios
    op.execute("""
        COMMENT ON TABLE auth.autorizacion_inicio IS 
        'Autorizaciones temporales de inicio de turno generadas via QR por el propietario'
    """)

    # ============================================================
    # PARTE 2: Tabla fleet.contrato_qr
    # ============================================================
    op.create_table(
        'contrato_qr',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('contrato_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('fecha_expiracion', sa.DateTime(), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('usos', sa.Integer(), server_default='0', nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', name='uq_contrato_qr_token'),
        sa.ForeignKeyConstraint(['contrato_id'], ['fleet.contrato_vehiculo.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['auth.usuario.id'], ondelete='SET NULL'),
        schema='fleet'
    )

    # Índices
    op.create_index('idx_contrato_qr_token', 'contrato_qr', ['token'], schema='fleet')
    op.create_index('idx_contrato_qr_contrato', 'contrato_qr', ['contrato_id'], schema='fleet')
    # Índice parcial: solo QRs activos
    op.create_index(
        'idx_contrato_qr_activos',
        'contrato_qr',
        ['contrato_id', 'fecha_expiracion'],
        schema='fleet',
        postgresql_where=sa.text('activo = true')
    )

    op.execute("""
        COMMENT ON TABLE fleet.contrato_qr IS 
        'QRs generados para contratos de vehículos, usados para trazabilidad y autorización de inicio de turno'
    """)

    # ============================================================
    # PARTE 3: Agregar columnas a public.escaneo_qr
    # (NOTA: la tabla está en schema 'public', NO en 'audit')
    # ============================================================
    
    # Usamos bloques DO para ser idempotentes (no fallan si la columna ya existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'escaneo_qr' AND column_name = 'contrato_id'
            ) THEN
                ALTER TABLE public.escaneo_qr ADD COLUMN contrato_id UUID;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'escaneo_qr' AND column_name = 'tipo_qr'
            ) THEN
                ALTER TABLE public.escaneo_qr ADD COLUMN tipo_qr VARCHAR(20) DEFAULT 'OPERATIVO';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'escaneo_qr' AND column_name = 'resultado'
            ) THEN
                ALTER TABLE public.escaneo_qr ADD COLUMN resultado VARCHAR(20);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'escaneo_qr' AND column_name = 'motivo'
            ) THEN
                ALTER TABLE public.escaneo_qr ADD COLUMN motivo TEXT;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'escaneo_qr' AND column_name = 'autorizacion_id'
            ) THEN
                ALTER TABLE public.escaneo_qr ADD COLUMN autorizacion_id UUID;
            END IF;
        END $$;
    """)

    # Foreign keys para las nuevas columnas (siempre que la columna exista)
    op.execute("""
        DO $$
        BEGIN
            -- FK a contrato_vehiculo
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_escaneo_qr_contrato' 
                  AND table_schema = 'public' AND table_name = 'escaneo_qr'
            ) THEN
                ALTER TABLE public.escaneo_qr 
                ADD CONSTRAINT fk_escaneo_qr_contrato 
                FOREIGN KEY (contrato_id) REFERENCES fleet.contrato_vehiculo(id) ON DELETE SET NULL;
            END IF;
            
            -- FK a autorizacion_inicio
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_escaneo_qr_autorizacion' 
                  AND table_schema = 'public' AND table_name = 'escaneo_qr'
            ) THEN
                ALTER TABLE public.escaneo_qr 
                ADD CONSTRAINT fk_escaneo_qr_autorizacion 
                FOREIGN KEY (autorizacion_id) REFERENCES auth.autorizacion_inicio(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)

    # Índices para escaneo_qr
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'public' AND tablename = 'escaneo_qr' AND indexname = 'idx_escaneo_qr_contrato'
            ) THEN
                CREATE INDEX idx_escaneo_qr_contrato ON public.escaneo_qr (contrato_id);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'public' AND tablename = 'escaneo_qr' AND indexname = 'idx_escaneo_qr_tipo'
            ) THEN
                CREATE INDEX idx_escaneo_qr_tipo ON public.escaneo_qr (tipo_qr);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'public' AND tablename = 'escaneo_qr' AND indexname = 'idx_escaneo_qr_autorizacion'
            ) THEN
                CREATE INDEX idx_escaneo_qr_autorizacion ON public.escaneo_qr (autorizacion_id);
            END IF;
        END $$;
    """)

    # CHECK constraints para integridad
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'chk_escaneo_qr_tipo' 
                  AND conrelid = 'public.escaneo_qr'::regclass
            ) THEN
                ALTER TABLE public.escaneo_qr 
                ADD CONSTRAINT chk_escaneo_qr_tipo 
                CHECK (tipo_qr IN ('OPERATIVO', 'COMERCIO', 'VEHICULO', 'OTRO'));
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'chk_escaneo_qr_resultado' 
                  AND conrelid = 'public.escaneo_qr'::regclass
            ) THEN
                ALTER TABLE public.escaneo_qr 
                ADD CONSTRAINT chk_escaneo_qr_resultado 
                CHECK (resultado IS NULL OR resultado IN ('EXITO', 'RECHAZADO', 'EXPIRADO', 'ERROR'));
            END IF;
        END $$;
    """)

    # ============================================================
    # PARTE 4: Corrección de usuario_rol - UNIQUE condicional
    # ============================================================
    
    # 4.1 Eliminar el constraint UNIQUE antiguo (creado en migración anterior)
    op.execute("ALTER TABLE auth.usuario_rol DROP CONSTRAINT IF EXISTS uq_usuario_rol_unico")
    
    # 4.2 Crear índice único condicional (solo para roles activos)
    # Esto permite que un usuario tenga múltiples roles históricos, pero solo uno activo por tipo
    op.execute("""
        CREATE UNIQUE INDEX uq_usuario_rol_activo 
        ON auth.usuario_rol (usuario_id, tipo_usuario_id) 
        WHERE activo = true
    """)


def downgrade() -> None:
    # ============================================================
    # REVERTIR PARTE 4: Restaurar constraint UNIQUE original
    # ============================================================
    op.execute("DROP INDEX IF EXISTS auth.uq_usuario_rol_activo")
    op.execute("""
        ALTER TABLE auth.usuario_rol 
        ADD CONSTRAINT uq_usuario_rol_unico UNIQUE (usuario_id, tipo_usuario_id)
    """)
    
    # ============================================================
    # REVERTIR PARTE 3: Eliminar columnas de public.escaneo_qr
    # ============================================================
    op.execute("DROP INDEX IF EXISTS public.idx_escaneo_qr_autorizacion")
    op.execute("DROP INDEX IF EXISTS public.idx_escaneo_qr_tipo")
    op.execute("DROP INDEX IF EXISTS public.idx_escaneo_qr_contrato")
    
    op.execute("ALTER TABLE public.escaneo_qr DROP CONSTRAINT IF EXISTS chk_escaneo_qr_resultado")
    op.execute("ALTER TABLE public.escaneo_qr DROP CONSTRAINT IF EXISTS chk_escaneo_qr_tipo")
    op.execute("ALTER TABLE public.escaneo_qr DROP CONSTRAINT IF EXISTS fk_escaneo_qr_autorizacion")
    op.execute("ALTER TABLE public.escaneo_qr DROP CONSTRAINT IF EXISTS fk_escaneo_qr_contrato")
    
    op.execute("ALTER TABLE public.escaneo_qr DROP COLUMN IF EXISTS autorizacion_id")
    op.execute("ALTER TABLE public.escaneo_qr DROP COLUMN IF EXISTS motivo")
    op.execute("ALTER TABLE public.escaneo_qr DROP COLUMN IF EXISTS resultado")
    op.execute("ALTER TABLE public.escaneo_qr DROP COLUMN IF EXISTS tipo_qr")
    op.execute("ALTER TABLE public.escaneo_qr DROP COLUMN IF EXISTS contrato_id")
    
    # ============================================================
    # REVERTIR PARTE 2: Eliminar fleet.contrato_qr
    # ============================================================
    op.drop_index('idx_contrato_qr_activos', table_name='contrato_qr', schema='fleet')
    op.drop_index('idx_contrato_qr_contrato', table_name='contrato_qr', schema='fleet')
    op.drop_index('idx_contrato_qr_token', table_name='contrato_qr', schema='fleet')
    op.drop_table('contrato_qr', schema='fleet')
    
    # ============================================================
    # REVERTIR PARTE 1: Eliminar auth.autorizacion_inicio
    # ============================================================
    op.drop_index('idx_autorizacion_inicio_chofer', table_name='autorizacion_inicio', schema='auth')
    op.drop_index('idx_autorizacion_inicio_contrato', table_name='autorizacion_inicio', schema='auth')
    op.drop_index('idx_autorizacion_inicio_expires', table_name='autorizacion_inicio', schema='auth')
    op.drop_index('idx_autorizacion_inicio_token', table_name='autorizacion_inicio', schema='auth')
    op.drop_table('autorizacion_inicio', schema='auth')