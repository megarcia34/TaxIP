"""
Payment and wallet routes
Recargas, pagos con wallet, webhooks Paypertic
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
import uuid as uuid_lib
import json

from app.database import get_db
from app.dependencies import get_current_user, get_current_passenger_user
from app.schemas.payment_schemas import (
    WalletBalanceResponse,
    TopUpRequest,
    TopUpResponse,
    PagarViajeConWalletRequest,
    PagarViajeConWalletResponse,
    TransaccionResponse,
    PaymentWebhookPayload
)

router = APIRouter(prefix="/api/pagos", tags=["Pagos"])


# ============================================
# WALLET (Billetera)
# ============================================

@router.get("/wallet/balance", response_model=WalletBalanceResponse)
async def obtener_saldo(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current wallet balance
    """
    user_id = current_user[0]
    
    # Check if wallet exists
    query = text("""
        SELECT saldo, moneda FROM payment.billetera
        WHERE usuario_id = :user_id
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        # Auto-create wallet if doesn't exist
        insert_query = text("""
            INSERT INTO payment.billetera (id, usuario_id, saldo, moneda, created_at, updated_at)
            VALUES (gen_random_uuid(), :user_id, 0, 'ARS', NOW(), NOW())
            RETURNING saldo, moneda
        """)
        
        result = await db.execute(insert_query, {"user_id": user_id})
        await db.commit()
        row = result.first()
    
    return WalletBalanceResponse(
        saldo=float(row[0]) if row[0] else 0,
        moneda=row[1]
    )


@router.post("/wallet/top-up", response_model=TopUpResponse)
async def recargar_wallet(
    request: TopUpRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request wallet top-up (returns Paypertic checkout URL)
    """
    user_id = current_user[0]
    
    # Get payment method ID
    metodo_query = text("""
        SELECT id FROM payment.metodo_pago
        WHERE nombre = :nombre
    """)
    
    result = await db.execute(metodo_query, {"nombre": request.metodo_pago})
    metodo_row = result.first()
    
    if not metodo_row:
        raise HTTPException(status_code=400, detail="Método de pago no válido")
    
    metodo_pago_id = metodo_row[0]
    
    # Create transaction record
    external_ref = str(uuid_lib.uuid4())
    transaccion_id = uuid_lib.uuid4()
    
    insert_query = text("""
        INSERT INTO payment.transaccion (
            id, billetera_id, viaje_id, metodo_pago_id, tipo, 
            monto, saldo_despues, estado, external_reference, created_at
        )
        SELECT 
            :transaccion_id, b.id, NULL, :metodo_pago_id, 'TOP_UP',
            :monto, b.saldo, 'PENDIENTE', :external_ref, NOW()
        FROM payment.billetera b
        WHERE b.usuario_id = :user_id
        RETURNING id
    """)
    
    result = await db.execute(insert_query, {
        "transaccion_id": transaccion_id,
        "metodo_pago_id": metodo_pago_id,
        "monto": request.monto,
        "external_ref": external_ref,
        "user_id": user_id
    })
    
    await db.commit()
    
    # Generate Paypertic checkout URL (simulation for now)
    # In production, call Paypertic API
    form_url = f"https://checkout.paypertic.com/simulate/{external_ref}?amount={request.monto}"
    
    return TopUpResponse(
        success=True,
        transaction_id=transaccion_id,
        form_url=form_url,
        monto=request.monto,
        message="Redirigiendo a pasarela de pagos"
    )


@router.post("/wallet/pay-trip", response_model=PagarViajeConWalletResponse)
async def pagar_viaje_con_wallet(
    request: PagarViajeConWalletRequest,
    current_user: tuple = Depends(get_current_passenger_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Pay a trip using wallet balance
    """
    user_id = current_user[0]
    
    # Get trip info
    trip_query = text("""
        SELECT id, precio_final, estado
        FROM trip.viaje_solicitado
        WHERE id = :viaje_id AND pasajero_id = :user_id AND estado = 'finalizado'
    """)
    
    result = await db.execute(trip_query, {
        "viaje_id": request.viaje_id,
        "user_id": user_id
    })
    trip_row = result.first()
    
    if not trip_row:
        raise HTTPException(
            status_code=404,
            detail="Viaje no encontrado o no finalizado"
        )
    
    monto = float(trip_row[1])
    
    # Get wallet and check balance
    wallet_query = text("""
        SELECT id, saldo FROM payment.billetera
        WHERE usuario_id = :user_id
        FOR UPDATE
    """)
    
    wallet_result = await db.execute(wallet_query, {"user_id": user_id})
    wallet_row = wallet_result.first()
    
    if not wallet_row:
        raise HTTPException(status_code=400, detail="Billetera no encontrada")
    
    wallet_id = wallet_row[0]
    saldo_actual = float(wallet_row[1])
    
    if saldo_actual < monto:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Disponible: ${saldo_actual}"
        )
    
    nuevo_saldo = saldo_actual - monto
    
    # Update wallet balance
    update_wallet = text("""
        UPDATE payment.billetera
        SET saldo = :nuevo_saldo, updated_at = NOW()
        WHERE id = :wallet_id
    """)
    
    await db.execute(update_wallet, {
        "nuevo_saldo": nuevo_saldo,
        "wallet_id": wallet_id
    })
    
    # Get metodo_pago_id for 'billetera'
    metodo_query = text("SELECT id FROM payment.metodo_pago WHERE nombre = 'billetera'")
    metodo_result = await db.execute(metodo_query)
    metodo_pago_id = metodo_result.scalar()
    
    # Create transaction
    insert_trans = text("""
        INSERT INTO payment.transaccion (
            id, billetera_id, viaje_id, metodo_pago_id, tipo,
            monto, saldo_despues, estado, created_at
        )
        VALUES (
            gen_random_uuid(), :wallet_id, :viaje_id, :metodo_pago_id, 'TRIP_PAYMENT',
            :monto, :saldo_despues, 'COMPLETADO', NOW()
        )
        RETURNING id
    """)
    
    trans_result = await db.execute(insert_trans, {
        "wallet_id": wallet_id,
        "viaje_id": request.viaje_id,
        "metodo_pago_id": metodo_pago_id,
        "monto": monto,
        "saldo_despues": nuevo_saldo
    })
    
    # Update trip as paid
    update_trip = text("""
        UPDATE trip.viaje_solicitado
        SET estado = 'pagado', updated_at = NOW()
        WHERE id = :viaje_id
    """)
    
    await db.execute(update_trip, {"viaje_id": request.viaje_id})
    
    await db.commit()
    
    return PagarViajeConWalletResponse(
        success=True,
        monto_pagado=monto,
        nuevo_saldo=nuevo_saldo,
        message=f"Viaje pagado con éxito. Nuevo saldo: ${nuevo_saldo}"
    )


@router.get("/wallet/transactions", response_model=list[TransaccionResponse])
async def obtener_transacciones(
    limit: int = 50,
    offset: int = 0,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get wallet transaction history
    """
    user_id = current_user[0]
    
    query = text("""
        SELECT 
            t.id,
            t.tipo,
            t.monto,
            t.saldo_despues,
            t.estado,
            t.descripcion,
            t.viaje_id,
            t.created_at
        FROM payment.transaccion t
        JOIN payment.billetera b ON b.id = t.billetera_id
        WHERE b.usuario_id = :user_id
        ORDER BY t.created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, {
        "user_id": user_id,
        "limit": limit,
        "offset": offset
    })
    rows = result.all()
    
    return [
        TransaccionResponse(
            id=row[0],
            tipo=row[1],
            monto=float(row[2]),
            saldo_despues=float(row[3]),
            estado=row[4],
            descripcion=row[5],
            viaje_id=row[6],
            created_at=row[7]
        )
        for row in rows
    ]


# ============================================
# PAYPERTIC WEBHOOK
# ============================================

@router.post("/paypertic/webhook")
async def paypertic_webhook(
    payload: PaymentWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for Paypertic payment gateway
    """
    # Find transaction by external reference
    query = text("""
        SELECT t.id, t.billetera_id, t.monto, t.estado
        FROM payment.transaccion t
        WHERE t.external_reference = :external_ref
    """)
    
    result = await db.execute(query, {"external_ref": payload.external_transaction_id})
    row = result.first()
    
    if not row:
        return {"status": "ignored", "message": "Transaction not found"}
    
    transaccion_id, billetera_id, monto, estado_actual = row
    
    # Idempotency: ignore if already processed
    if estado_actual != "PENDIENTE":
        return {"status": "ignored", "message": "Already processed"}
    
    if payload.status == "APPROVED":
        # Update wallet balance
        update_wallet = text("""
            UPDATE payment.billetera
            SET saldo = saldo + :monto, updated_at = NOW()
            WHERE id = :billetera_id
            RETURNING saldo
        """)
        
        wallet_result = await db.execute(update_wallet, {
            "monto": float(monto),
            "billetera_id": billetera_id
        })
        nuevo_saldo = wallet_result.scalar()
        
        # Update transaction
        update_trans = text("""
            UPDATE payment.transaccion
            SET estado = 'COMPLETADO',
                saldo_despues = :nuevo_saldo,
                provider_id = :provider_id,
                provider_data = :provider_data,
                descripcion = 'Recarga aprobada'
            WHERE id = :transaccion_id
        """)
        
        await db.execute(update_trans, {
            "nuevo_saldo": nuevo_saldo,
            "provider_id": payload.provider_id,
            "provider_data": json.dumps(payload.dict()),
            "transaccion_id": transaccion_id
        })
        
    else:
        # Mark as failed
        update_trans = text("""
            UPDATE payment.transaccion
            SET estado = 'FALLIDO',
                provider_data = :provider_data,
                descripcion = 'Pago rechazado'
            WHERE id = :transaccion_id
        """)
        
        await db.execute(update_trans, {
            "provider_data": json.dumps(payload.dict()),
            "transaccion_id": transaccion_id
        })
    
    await db.commit()
    
    return {"status": "processed", "message": f"Payment {payload.status}"}