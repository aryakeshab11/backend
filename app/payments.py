from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request

try:
    import stripe
except Exception:
    stripe = None

from app.db import SessionLocal, init_db
from app.models import License

router = APIRouter(prefix="/payments", tags=["payments"]) 

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if stripe and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Ensure DB tables exist
try:
    init_db()
except Exception:
    pass


def _create_license(session, **kwargs) -> str:
    key = uuid.uuid4().hex
    lic = License(
        license_key=key,
        user_id=kwargs.get("user_id"),
        provider=kwargs.get("provider"),
        amount_usd=kwargs.get("amount_usd", 0.0),
        currency=kwargs.get("currency", "USD"),
        amount_local=kwargs.get("amount_local"),
        session_id=kwargs.get("session_id"),
        trial_expires_at=kwargs.get("trial_expires_at"),
        active=kwargs.get("active", True),
    )
    session.add(lic)
    session.commit()
    session.refresh(lic)
    return lic.license_key


@router.post("/checkout")
async def create_checkout(request: Request):
    if stripe is None:
        raise HTTPException(status_code=503, detail="Stripe library not configured on server.")
    body = await request.json()
    body.get("country") or "US"
    price_usd_cents = 100
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": "AI-Health-Coach Lifetime"}, "unit_amount": price_usd_cents}, "quantity": 1}],
            mode="payment",
            success_url=body.get("success_url") or "https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=body.get("cancel_url") or "https://example.com/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    if stripe is None:
        raise HTTPException(status_code=503, detail="Stripe library not configured on server.")
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    if event["type"] == "checkout.session.completed":
        obj = event["data"]["object"]
        db = SessionLocal()
        try:
            amount_usd = 0.0
            currency = obj.get("currency") or "usd"
            session_id = obj.get("id")
            if obj.get("amount_total"):
                amount_usd = obj.get("amount_total") / 100.0
            _create_license(db, provider="stripe", amount_usd=amount_usd, currency=currency, session_id=session_id)
        finally:
            db.close()
    return {"status": "ok"}


@router.post("/trial")
async def start_trial(request: Request):
    body = await request.json()
    user_id = body.get("user_id") or "anonymous"
    db = SessionLocal()
    try:
        trial_expires = datetime.utcnow() + timedelta(days=7)
        key = _create_license(db, provider="trial", user_id=user_id, amount_usd=0.0, currency="USD", trial_expires_at=trial_expires)
    finally:
        db.close()
    return {"license_key": key, "trial_expires_at": trial_expires.isoformat()}
