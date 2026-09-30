"""
Autenticación WebSocket para TaxIP.

Valida el JWT recibido en el query string del handshake y resuelve
los datos del usuario (user_id, rol, control_base_id).

Estrategia:
1. Decodificar el JWT con app.core.security.decode_token
2. Verificar que user_id del path coincida con el 'sub' del token
3. Extraer 'tipo' (rol) y 'control_base_id' del JWT
4. Si falta control_base_id, consultar la BD como fallback
5. Si el usuario está inactivo, rechazar
6. Si falta control_base_id (y no es super_admin), rechazar
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import WebSocket
from sqlalchemy import text

from app.core.security import decode_token
from app.database import AsyncSessionLocal
from app.websocket.events import WsCloseCode

logger = logging.getLogger(__name__)


class WsAuthError(Exception):
    """Error de autenticación WebSocket."""
    def __init__(self, message: str, code: int = WsCloseCode.UNAUTHORIZED):
        self.message = message
        self.code = code
        super().__init__(message)


async def authenticate_ws(
    token: Optional[str],
    user_id_from_path: str,
) -> dict:
    """
    Autentica un WebSocket a partir del token JWT.

    Args:
        token: JWT del query string (puede ser None).
        user_id_from_path: user_id del path URL.

    Returns:
        dict con {user_id, rol, control_base_id, email}

    Raises:
        WsAuthError: si el token es inválido, expirado, o no coincide.
    """
    # 1. Token obligatorio
    if not token:
        raise WsAuthError("Token ausente", WsCloseCode.UNAUTHORIZED)

    # 2. Decodificar JWT
    payload = decode_token(token)
    if not payload:
        raise WsAuthError("Token inválido o expirado", WsCloseCode.UNAUTHORIZED)

    # 3. Validar tipo de token
    if payload.get("type") != "access":
        raise WsAuthError("Se requiere un access token", WsCloseCode.UNAUTHORIZED)

    # 4. Validar que el sub coincida con el user_id del path
    sub = payload.get("sub")
    if not sub or str(sub) != str(user_id_from_path):
        logger.warning(
            f"WS auth: user_id mismatch. Path={user_id_from_path}, sub={sub}"
        )
        raise WsAuthError(
            "user_id del path no coincide con el token",
            WsCloseCode.FORBIDDEN,
        )

    # 5. Extraer rol y control_base_id del JWT
    rol = payload.get("tipo")
    control_base_id = payload.get("control_base_id")

    # 6. Validar rol
    roles_validos = {"chofer", "pasajero", "empleado", "propietario"}
    if rol not in roles_validos:
        raise WsAuthError(
            f"Rol '{rol}' no soportado en WebSocket",
            WsCloseCode.INVALID_ROLE,
        )

    # 7. Fallback a BD si falta control_base_id o para validar activo
    user_uuid = UUID(str(sub))

    async with AsyncSessionLocal() as db:
        row = await db.execute(
            text("""
                SELECT id, email, activo, control_base_id
                FROM auth.usuario
                WHERE id = :uid
                LIMIT 1
            """),
            {"uid": user_uuid},
        )
        usuario = row.fetchone()

        if not usuario:
            raise WsAuthError("Usuario no encontrado", WsCloseCode.UNAUTHORIZED)

        if not usuario.activo:
            raise WsAuthError("Usuario inactivo", WsCloseCode.UNAUTHORIZED)

        # Si el JWT no traía control_base_id, usar el de la BD
        if not control_base_id and usuario.control_base_id:
            control_base_id = str(usuario.control_base_id)

        email = usuario.email

    # 8. Validar control_base_id (excepto super_admin)
    # Opción A: bloqueo estricto para garantizar aislamiento multi-tenant
    if rol != "super_admin" and not control_base_id:
        logger.warning(
            f"WS auth: usuario {user_uuid} sin control_base_id asignado"
        )
        raise WsAuthError(
            "Usuario sin tenant asignado",
            WsCloseCode.UNAUTHORIZED,
        )

    return {
        "user_id": str(sub),
        "rol": rol,
        "control_base_id": str(control_base_id) if control_base_id else None,
        "email": email,
    }
