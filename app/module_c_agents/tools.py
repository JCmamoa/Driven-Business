import httpx
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Product
from app.observability.metrics import AGENT_ACTIONS


async def lookup_order(order_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"https://erp.example.com/orders/{order_id}", timeout=5)
            AGENT_ACTIONS.labels(tool="lookup_order", status="ok").inc()
            return r.json()
        except Exception:
            AGENT_ACTIONS.labels(tool="lookup_order", status="error").inc()
            raise


async def generate_return_label(order_id: str) -> dict:
    AGENT_ACTIONS.labels(tool="generate_return_label", status="ok").inc()
    return {"label_url": f"https://carrier.example.com/label/{order_id}.pdf"}


async def issue_exchange_coupon(order_id: str, amount: float) -> dict:
    AGENT_ACTIONS.labels(tool="issue_coupon", status="ok").inc()
    return {"coupon_code": f"EXCH-{order_id[-6:]}"}


async def issue_refund(order_id: str, amount: float) -> dict:
    AGENT_ACTIONS.labels(tool="issue_refund", status="ok").inc()
    return {"refund_id": f"RF-{order_id[-6:]}", "amount": amount}


async def check_product_stock(sku: str) -> dict:
    with SessionLocal() as session:
        p = session.scalar(select(Product).where(Product.sku == sku))
        if not p:
            return {"available": False}
        return {"available": True, "price": float(p.price)}