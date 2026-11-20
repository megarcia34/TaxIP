"""fase1_auth_fleet_turnos_manual

Revision ID: 605c45669a36
Revises: 9cde8795c601
Create Date: 2026-08-24 19:46:41.268565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '605c45669a36'
down_revision: Union[str, Sequence[str], None] = '9cde8795c601'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FASE 1: AUTH + FLEET + TURNOS
    SOLO AGREGA LO QUE FALTA - NO ELIMINA NADA
    """
    
    # ============================================================
    # 1. AUTH - SOLO LO QUE FALTA
    # ============================================================
    
    # NOTA: Las columnas de suspensión (fecha_suspension, motivo_suspension, suspendido_por)
    # YA EXISTEN en auth.usuario. No es necesario agregarlas.
    # La FK suspendido_por -> auth.usuario.id YA EXISTE.
    
    # NOTA: Las columnas de perfil_general (fecha_nacimiento, barrio, codigo_postal,
    # tipo_conductor, agencia, updated_at) YA EXISTEN en auth.perfil_general.
    # No es necesario agregarlas.
    
    # 1.1 auth.usuario_rol - agregar columna control_base_id (si no existe)
    # Verificamos si existe con un try/except
    try:
        op.add_column('usuario_rol', sa.Column('control_base_id', UUID(as_uuid=True), nullable=True), schema='auth')
        op.create_foreign_key(
            op.f('fk_usuario_rol_control_base_id_control_base'),
            'usuario_rol', 'control_base',
            ['control_base_id'], ['id'],
            source_schema='auth', referent_schema='tenant',
            ondelete='SET NULL'
        )
    except Exception as e:
        # Si la columna ya existe, ignoramos el error
        print(f"INFO: {e}")
    
    # ============================================================
    # 2. FLEET - MODELOS QUE YA EXISTEN
    # ============================================================
    
    # NOTA: contrato_qr, marca, modelo, documentos_chofer, foto_vehiculo,
    # notificacion_vencimiento YA EXISTEN en la BD.
    # No es necesario crearlos.
    
    # ============================================================
    # 3. TURNOS - MODELOS QUE YA EXISTEN
    # ============================================================
    
    # NOTA: turno_empleado y autorizacion_inicio YA EXISTEN en la BD.
    # No es necesario crearlos.
    
    # ============================================================
    # 4. PUBLIC - COMERCIO Y ESCANEO_QR
    # ============================================================
    
    # NOTA: comercio y escaneo_qr YA EXISTEN en la BD.
    # No es necesario crearlos.
    
    # ============================================================
    # 5. TRIP - RESERVA
    # ============================================================
    
    # NOTA: reserva YA EXISTE en la BD.
    # No es necesario crearla.
    
    # ============================================================
    # 6. PAYMENT - FACTURA_EMPRESA Y PAGO_EMPRESA
    # ============================================================
    
    # NOTA: factura_empresa y pago_empresa YA EXISTEN en la BD.
    # No es necesario crearlos.
    
    # ============================================================
    # 7. TENANT - FACTURA
    # ============================================================
    
    # NOTA: factura YA EXISTE en la BD.
    # No es necesario crearla.
    
    pass


def downgrade() -> None:
    """
    REVERTIR CAMBIOS DE LA FASE 1
    """
    
    # Eliminar foreign key de auth.usuario_rol
    try:
        op.drop_constraint(op.f('fk_usuario_rol_control_base_id_control_base'), 'usuario_rol', schema='auth', type_='foreignkey')
        op.drop_column('usuario_rol', 'control_base_id', schema='auth')
    except Exception as e:
        print(f"INFO: {e}")
    
    pass