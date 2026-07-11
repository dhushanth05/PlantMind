import logging

from fastapi import APIRouter, HTTPException, status

from app.domain.admin.schemas import FactoryResetResponse
from app.services.factory_reset_service import FactoryResetService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.delete("/factory-reset", response_model=FactoryResetResponse)
async def factory_reset() -> FactoryResetResponse:
    try:
        return await FactoryResetService().reset()
    except RuntimeError as exc:
        logger.warning("factory_reset_rejected", extra={"reason": str(exc)})
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("factory_reset_failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Factory reset failed") from exc
