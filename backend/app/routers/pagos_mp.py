from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID
import uuid as uuid_lib

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.mp_schemas import (
    MPAuthorizeResponse,
    MPCobroDirectoRequest,
    MPCobroDirectoResponse,
    MPVinculacionStatusResponse,
    MPWebhookResponse,
)
from app.services.mercadopago_service import (
    MercadoPagoError,
    build_authorization_url,
    create_direct_charge_preference,
    exchange_authorization_code,
    fetch_payment_by_id,
    parse_oauth_state,
    upsert_vinculacion_from_oauth,
    verify_webhook_signature,
)
from app.models.payment import VinculacionMP


router = APIRouter(prefix="/api/pagos", tags=["MercadoPago"])


@router.get("/mp/authorize", response_model=MPAuthorizeResponse)
async def mp_authorize(
    current_user: tuple = Depends(get_current_user),
):
    usuario_id = current_user[0]
    try:
        auth_url, state = build_authorization_url(usuario_id)
    except MercadoPagoError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return MPAuthorizeResponse(authorization_url=auth_url, state=state)


@router.get("/mp/callback", response_class=HTMLResponse)
async def mp_callback(
    code: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    error: Optional[str] = Query(default=None),
    error_description: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mercado Pago rechazo la autorizacion: {error} ({error_description or ''})",
        )
    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parametros code y state son obligatorios en callback",
        )

    try:
        usuario_id = parse_oauth_state(state)
        token_data = await exchange_authorization_code(code)
        vinculacion = await upsert_vinculacion_from_oauth(db, usuario_id, token_data)
    except MercadoPagoError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    html = f"""
    <!doctype html>
    <html lang="es">
      <head><meta charset="utf-8"><title>TaxIP - Cuenta vinculada</title></head>
      <body style="font-family: sans-serif; padding: 2rem;">
        <h2>Cuenta de Mercado Pago vinculada</h2>
        <p>Usuario TaxIP: <strong>{usuario_id}</strong></p>
        <p>Cuenta MP ID: <strong>{vinculacion.mp_user_id}</strong></p>
        <p>Estado: <strong>{vinculacion.estado}</strong></p>
        <p>Ya podes volver a TaxIP para recibir cobros directos.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)


@router.get("/mp/status", response_model=MPVinculacionStatusResponse)
async def mp_status(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    usuario_id = current_user[0]
    stmt = select(VinculacionMP).where(VinculacionMP.usuario_id == usuario_id)
    vinculacion = (await db.execute(stmt)).scalar_one_or_none()

    if vinculacion is None:
        return MPVinculacionStatusResponse(vinculada=False)

    return MPVinculacionStatusResponse(
        vinculada=vinculacion.estado == "vinculada",
        estado=vinculacion.estado,
        mp_user_id=vinculacion.mp_user_id,
        mp_email=vinculacion.mp_email,
        mp_nickname=vinculacion.mp_nickname,
        expires_at=vinculacion.expires_at,
    )


@router.post("/mp/cobro-directo", response_model=MPCobroDirectoResponse)
async def mp_cobro_directo(
    request: MPCobroDirectoRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    external_ref = request.external_reference or f"taxip_cobro_{uuid_lib.uuid4().hex[:16]}"
    
    # Si viene viaje_id, validamos el propietario real desde la BD
    cb_id = None
    if request.viaje_id is not None:
        prop_res = await db.execute(
            text("""
                SELECT vs.control_base_id, v.propietario_id
                FROM trip.viaje_solicitado vs
                LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
                WHERE vs.id = :viaje_id
            """),
            {"viaje_id": request.viaje_id},
        )
        prop_row = prop_res.first()
        if not prop_row or not prop_row[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Viaje no encontrado para asociar el cobro",
            )
        cb_id = prop_row[0]
        propietario_real = prop_row[1]

        # Validación de seguridad: evitar que se cobre a otro propietario
        if propietario_real is not None and request.propietario_id != propietario_real:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El propietario_id no coincide con el propietario del vehículo del viaje",
            )

    try:
        result = await create_direct_charge_preference(
            db=db,
            propietario_id=request.propietario_id,
            monto=float(request.monto),
            titulo=request.titulo,
            external_reference=external_ref,
            payer_email=request.payer_email,
        )
    except MercadoPagoError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    pref = result["preference"]
    vinculacion: VinculacionMP = result["vinculacion"]
    preference_id = str(pref.get("id") or "")
    init_point = str(pref.get("init_point") or "")
    sandbox_init_point = pref.get("sandbox_init_point")

    if not preference_id or not init_point:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Mercado Pago no devolvio preference_id o init_point",
        )

    # Registrar/actualizar qr_cobro con pasarela mercadopago
    if request.viaje_id is not None and cb_id:
        await db.execute(
            text("""
                INSERT INTO payment.qr_cobro (
                    id, viaje_id, token, monto, pasarela, estado,
                    url_pago, id_transaccion_externa, creado_en, expira_en, control_base_id
                )
                VALUES (
                    gen_random_uuid(), :viaje_id, :token, :monto, 'mercadopago', 'pendiente',
                    :url_pago, :ext_ref, NOW(), NOW() + INTERVAL '30 minutes', :cb_id
                )
            """),
            {
                "viaje_id": request.viaje_id,
                "token": preference_id,
                "monto": request.monto,
                "url_pago": init_point,
                "ext_ref": external_ref,
                "cb_id": cb_id,
            },
        )
        await db.commit()

    return MPCobroDirectoResponse(
        preference_id=preference_id,
        init_point=init_point,
        sandbox_init_point=sandbox_init_point,
        external_reference=external_ref,
        propietario_id=request.propietario_id,
        mp_user_id=vinculacion.mp_user_id,
        excluded_payment_types=result["excluded_payment_types"],
        monto=request.monto,
        moneda="ARS",
    )


@router.post("/webhook/mercadopago", response_model=MPWebhookResponse)
async def mp_webhook(
    request: Request,
    x_signature: Optional[str] = Header(default=None, alias="x-signature"),
    x_request_id: Optional[str] = Header(default=None, alias="x-request-id"),
    db: AsyncSession = Depends(get_db),
):
    query_params = dict(request.query_params)
    body: dict[str, Any] = {}
    try:
        raw_body = await request.body()
        if raw_body:
            body = await request.json()
    except Exception:
        body = {}

    topic = query_params.get("type") or query_params.get("topic") or body.get("type") or body.get("topic")
    data_id = (
        query_params.get("data.id")
        or query_params.get("id")
        or (body.get("data", {}) or {}).get("id")
        or body.get("id")
    )
    data_id_str = str(data_id) if data_id is not None else None

    if not verify_webhook_signature(x_signature, x_request_id, data_id_str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma de webhook de Mercado Pago invalida o faltante",
        )

    if topic == "payment" and data_id_str:
        # 1. Resolver vinculacion por el mp_user_id que inyectamos en la notification_url
        mp_user_id_raw = query_params.get("mp_user_id")
        vinc: Optional[VinculacionMP] = None
        if mp_user_id_raw:
            try:
                mp_user_id_int = int(mp_user_id_raw)
            except ValueError:
                mp_user_id_int = None
            if mp_user_id_int is not None:
                vinc = (
                    await db.execute(
                        select(VinculacionMP).where(
                            VinculacionMP.mp_user_id == mp_user_id_int,
                            VinculacionMP.estado == "vinculada",
                        )
                    )
                ).scalar_one_or_none()

        # Fallback: si por alguna razon no vino el mp_user_id, intentar con la unica activa
        if vinc is None:
            vinc = (
                await db.execute(
                    select(VinculacionMP).where(VinculacionMP.estado == "vinculada").limit(1)
                )
            ).scalar_one_or_none()

        if vinc is None:
            # Devolvemos 200 para que MP no reintente en loop infinito
            return MPWebhookResponse(
                received=True,
                signature_valid=True,
                topic=topic,
                resource_id=data_id_str,
                detail="sin vinculacion activa para resolver el pago",
            )

        payment_info = await fetch_payment_by_id(data_id_str, access_token=vinc.access_token)
        mp_status = payment_info.get("status")
        ext_ref = payment_info.get("external_reference")

        if ext_ref and mp_status == "approved":
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            await db.execute(
                text("""
                    UPDATE payment.qr_cobro
                    SET estado = 'pagado',
                        pagado_en = COALESCE(pagado_en, :pagado_en)
                    WHERE id_transaccion_externa = :ext_ref
                      AND estado <> 'pagado'
                """),
                {
                    "pagado_en": now_naive,
                    "ext_ref": ext_ref,
                },
            )
            await db.commit()

        return MPWebhookResponse(
            received=True,
            signature_valid=True,
            topic=topic,
            resource_id=data_id_str,
            detail=f"payment_status={mp_status or 'unknown'}",
        )

    return MPWebhookResponse(
        received=True,
        signature_valid=True,
        topic=topic,
        resource_id=data_id_str,
        detail="evento ignorado o sin accion adicional",
    )