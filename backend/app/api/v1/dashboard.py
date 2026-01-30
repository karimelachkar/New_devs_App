from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    # FIX Bug 3: Use Decimal for precise financial calculations.
    # Converting directly to float loses precision (e.g., 333.333 + 333.333 + 333.334
    # may become 999.9999... or 1000.0001... in float arithmetic).
    # Instead, use Decimal to round to exactly 2 decimal places first.
    from decimal import Decimal, ROUND_HALF_UP
    
    total_decimal = Decimal(revenue_data['total'])
    # Round to 2 decimal places for currency display using standard rounding
    total_rounded = total_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": float(total_rounded),  # Convert to float only after precise rounding
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
