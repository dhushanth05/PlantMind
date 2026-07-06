from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.assets.schemas import AssetDigitalTwin
from app.services.assets.digital_twin_service import DigitalTwinService

router = APIRouter()


def get_digital_twin_service() -> DigitalTwinService:
    return DigitalTwinService()


@router.get("/{asset_id}/digital-twin", response_model=AssetDigitalTwin)
async def get_asset_digital_twin(
    asset_id: str,
    service: Annotated[DigitalTwinService, Depends(get_digital_twin_service)],
) -> AssetDigitalTwin:
    try:
        return await service.get_digital_twin(asset_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

