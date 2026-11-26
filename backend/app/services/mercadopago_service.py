from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from typing import Any, Optional
from urllib.parse import urlencode
from uuid import UUID

import httpx
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.payment import VinculacionMP


MP_AUTH_URL = "https://auth.mercadopago.com.ar/authorization"
MP_TOKEN_URL = "https://api.mercadopago.com/oauth/token"
MP_USERS_ME_URL = "https://api.mercadopago.com/users/me"
MP_PREFERENCES_URL = "https://api.mercadopago.com/checkout/preferences"
MP_PAYMENTS_URL = "https://api.mercadopago.com/v1/payments"


class MercadoPagoError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


def _state_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key=settings.SECRET_KEY, salt="taxip-mp-oauth-v1")


def build_oauth_state(usuario_id: UUID) -> str:
    return _state_serializer().dumps({"usuario_id": str(usuario_id)})


def parse_oauth_state(state: str, max_age_seconds: int = 900) -> UUID:
    try:
        data = _state_serializer().loads(state, max_age=max_age_seconds)
        return UUID(str(data["usuario_id"]))
    except (BadSignature, SignatureExpired, KeyError, ValueError) as exc:
        raise MercadoPagoError("Estado OAuth invalido o expirado", status_code=400) from exc


def build_authorization_url(usuario_id: UUID) -> tuple[str, str]:
    client_id = settings.MP_CLIENT_ID or settings.MP_APP_ID
    if not client_id or not settings.MP_REDIRECT_URI:
        raise MercadoPagoError("Falta configurar MP_CLIENT_ID/MP_APP_ID o MP_REDIRECT_URI", status_code=500)

    state = build_oauth_state(usuario_id)
    params = {
        "client_id": client_id,
        "response_type": "code",
        "platform_id": "mp",
        "redirect_uri": settings.MP_REDIRECT_URI,
        "state": state,
    }
    return f"{MP_AUTH_URL}?{urlencode(params)}", state


def _compute_expires_at(expires_in: Optional[int]) -> Optional[datetime]:
    if not expires_in:
        return None
    # Guardamos en naive UTC alineado a TIMESTAMP WITHOUT TIME ZONE
    dt_utc = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
    return dt_utc.replace(tzinfo=None)


async def exchange_authorization_code(code: str) -> dict[str, Any]:
    client_id = settings.MP_CLIENT_ID or settings.MP_APP_ID
    if not client_id or not settings.MP_CLIENT_SECRET or not settings.MP_REDIRECT_URI:
        raise MercadoPagoError("Faltan credenciales OAuth de Mercado Pago en settings", status_code=500)

    payload = {
        "client_id": client_id,
        "client_secret": settings.MP_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.MP_REDIRECT_URI,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(MP_TOKEN_URL, data=payload)
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400:
            raise MercadoPagoError(
                data.get("message") or "Error al intercambiar code OAuth en Mercado Pago",
                status_code=502,
                payload=data,
            )
        return data


async def refresh_oauth_token(refresh_token: str) -> dict[str, Any]:
    client_id = settings.MP_CLIENT_ID or settings.MP_APP_ID
    payload = {
        "client_id": client_id,
        "client_secret": settings.MP_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(MP_TOKEN_URL, data=payload)
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400:
            raise MercadoPagoError(
                data.get("message") or "Error al refrescar token OAuth de Mercado Pago",
                status_code=502,
                payload=data,
            )
        return data


async def fetch_mp_user_profile(access_token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(MP_USERS_ME_URL, headers=headers)
        if resp.status_code >= 400:
            return {}
        return resp.json() if resp.content else {}


async def upsert_vinculacion_from_oauth(
    db: AsyncSession,
    usuario_id: UUID,
    token_data: dict[str, Any],
) -> VinculacionMP:
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    mp_user_id = token_data.get("user_id")

    if not access_token or not refresh_token or not mp_user_id:
        raise MercadoPagoError("Respuesta OAuth incompleta de Mercado Pago", status_code=502, payload=token_data)

    try:
        mp_user_id = int(mp_user_id)
    except ValueError as exc:
        raise MercadoPagoError("user_id de Mercado Pago inválido", status_code=502) from exc

    profile = await fetch_mp_user_profile(access_token)
    mp_email = profile.get("email")
    mp_nickname = profile.get("nickname")
    public_key = token_data.get("public_key")
    token_type = token_data.get("token_type") or "Bearer"
    expires_in = token_data.get("expires_in")
    scope = token_data.get("scope")
    expires_at = _compute_expires_at(expires_in)
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)

    stmt = select(VinculacionMP).where(VinculacionMP.usuario_id == usuario_id)
    vinculacion = (await db.execute(stmt)).scalar_one_or_none()

    if vinculacion is None:
        vinculacion = VinculacionMP(
            usuario_id=usuario_id,
            mp_user_id=mp_user_id,
            mp_email=mp_email,
            mp_nickname=mp_nickname,
            access_token=access_token,
            refresh_token=refresh_token,
            public_key=public_key,
            token_type=token_type,
            expires_in=expires_in,
            expires_at=expires_at,
            scope=scope,
            estado="vinculada",
            ultimo_error=None,
            created_at=now_naive,
            updated_at=now_naive,
        )
        db.add(vinculacion)
    else:
        vinculacion.mp_user_id = mp_user_id
        vinculacion.mp_email = mp_email or vinculacion.mp_email
        vinculacion.mp_nickname = mp_nickname or vinculacion.mp_nickname
        vinculacion.access_token = access_token
        vinculacion.refresh_token = refresh_token
        vinculacion.public_key = public_key or vinculacion.public_key
        vinculacion.token_type = token_type
        vinculacion.expires_in = expires_in
        vinculacion.expires_at = expires_at
        vinculacion.scope = scope or vinculacion.scope
        vinculacion.estado = "vinculada"
        vinculacion.ultimo_error = None
        vinculacion.updated_at = now_naive

    await db.commit()
    await db.refresh(vinculacion)
    return vinculacion


async def get_valid_access_token(db: AsyncSession, propietario_id: UUID) -> VinculacionMP:
    stmt = select(VinculacionMP).where(VinculacionMP.usuario_id == propietario_id)
    vinculacion = (await db.execute(stmt)).scalar_one_or_none()

    if vinculacion is None or vinculacion.estado != "vinculada":
        raise MercadoPagoError(
            "El propietario no tiene una cuenta de Mercado Pago vinculada activa",
            status_code=400,
        )

    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    needs_refresh = (
        vinculacion.expires_at is not None
        and vinculacion.expires_at <= (now_naive + timedelta(minutes=5))
    )

    if needs_refresh and vinculacion.refresh_token:
        try:
            refreshed = await refresh_oauth_token(vinculacion.refresh_token)
            return await upsert_vinculacion_from_oauth(db, propietario_id, refreshed)
        except MercadoPagoError as exc:
            vinculacion.estado = "error"
            vinculacion.ultimo_error = exc.message
            vinculacion.updated_at = now_naive
            await db.commit()
            raise

    return vinculacion


def get_excluded_payment_types() -> list[dict[str, str]]:
    raw = (settings.MP_EXCLUDED_PAYMENT_TYPES or "credit_card").split(",")
    ids = [item.strip() for item in raw if item.strip()]
    if "credit_card" not in ids:
        ids.append("credit_card")
    return [{"id": payment_type_id} for payment_type_id in ids]


async def create_direct_charge_preference(
    db: AsyncSession,
    propietario_id: UUID,
    monto: float,
    titulo: str,
    external_reference: str,
    payer_email: Optional[str] = None,
) -> dict[str, Any]:
    """
    Crea una preferencia de cobro directo usando el access_token OAuth del
    propietario (el dinero ingresa directo a la cuenta MP vinculada del
    propietario) y excluye tarjetas de credito.
    """
    vinculacion = await get_valid_access_token(db, propietario_id)
    excluded_types = get_excluded_payment_types()

    preference_payload: dict[str, Any] = {
        "items": [
            {
                "title": titulo,
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(monto),
            }
        ],
        "external_reference": external_reference,
        "payment_methods": {
            "excluded_payment_types": excluded_types,
            "installments": 1,
        },
    }

    if settings.MP_WEBHOOK_URL:
        sep = "&" if "?" in settings.MP_WEBHOOK_URL else "?"
        preference_payload["notification_url"] = (
            f"{settings.MP_WEBHOOK_URL}{sep}mp_user_id={vinculacion.mp_user_id}"
        )

    if payer_email:
        preference_payload["payer"] = {"email": payer_email}

    headers = {
        "Authorization": f"Bearer {vinculacion.access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(MP_PREFERENCES_URL, headers=headers, json=preference_payload)
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400:
            raise MercadoPagoError(
                data.get("message") or "Error al crear preferencia de cobro directo en Mercado Pago",
                status_code=502,
                payload=data,
            )

    return {
        "vinculacion": vinculacion,
        "preference": data,
        "excluded_payment_types": [item["id"] for item in excluded_types],
    }


def verify_webhook_signature(
    x_signature: Optional[str],
    x_request_id: Optional[str],
    data_id: Optional[str],
) -> bool:
    """
    Valida la firma HMAC-SHA256 enviada por Mercado Pago en el header x-signature
    (formato: 'ts=<timestamp>,v1=<hash>'). Si MP_WEBHOOK_SECRET no esta configurado,
    rechaza por seguridad en entornos que requieran firma.
    """
    if not settings.MP_WEBHOOK_SECRET or not x_signature or not data_id:
        return False

    parts: dict[str, str] = {}
    for token in x_signature.split(","):
        if "=" in token:
            k, v = token.split("=", 1)
            parts[k.strip()] = v.strip()

    ts = parts.get("ts")
    v1 = parts.get("v1")
    if not ts or not v1:
        return False

    manifest_parts = [f"id:{data_id.lower()}"]
    if x_request_id:
        manifest_parts.append(f"request-id:{x_request_id}")
    manifest_parts.append(f"ts:{ts}")
    manifest = ";".join(manifest_parts) + ";"

    expected_hmac = hmac.new(
        settings.MP_WEBHOOK_SECRET.encode("utf-8"),
        msg=manifest.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_hmac, v1.lower())


async def fetch_payment_by_id(payment_id: str, access_token: Optional[str] = None) -> dict[str, Any]:
    if not access_token:
        raise MercadoPagoError(
            "fetch_payment_by_id requiere access_token del propietario vinculado",
            status_code=500,
        )
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{MP_PAYMENTS_URL}/{payment_id}", headers=headers)
        if resp.status_code >= 400:
            return {}
        return resp.json() if resp.content else {}


def serialize_raw_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)