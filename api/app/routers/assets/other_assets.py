"""OtherAsset (asset category) CRUD endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.assets.other_asset import (
    OtherAssetCreate,
    OtherAssetItem,
    OtherAssetRead,
    OtherAssetUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.asset_service import (
    create_other_asset,
    delete_other_asset,
    list_other_asset_items,
    list_other_assets,
    update_other_asset,
)

router = APIRouter()


@router.get(
    "",
    summary="List asset categories",
    description="Return all asset categories ordered by asset_index ascending (drives dropdown order).",
    response_model=ApiResponse[list[OtherAssetRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_other_assets_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[OtherAssetRead]]:
    rows = list_other_assets(session)
    return ApiResponse(data=[OtherAssetRead.model_validate(r, from_attributes=True) for r in rows])


@router.get(
    "/items",
    summary="List distinct asset types",
    description="Return the distinct asset_type values currently in use.",
    response_model=ApiResponse[list[OtherAssetItem]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_other_asset_items_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[OtherAssetItem]]:
    rows = list_other_asset_items(session)
    return ApiResponse(data=rows)


@router.post(
    "",
    summary="Create asset category",
    description="Create a new asset category. If asset_index is omitted, the server assigns max(asset_index)+1.",
    response_model=ApiResponse[OtherAssetRead],
    responses={
        409: error_response("Duplicate asset_id", error_payload="Duplicate asset_id"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_other_asset_endpoint(
    payload: OtherAssetCreate, session: Session = Depends(get_session)
) -> ApiResponse[OtherAssetRead]:
    row = create_other_asset(session, payload)
    return ApiResponse(data=OtherAssetRead.model_validate(row, from_attributes=True))


@router.put(
    "/{asset_id}",
    summary="Update asset category",
    description="Update an asset category by id; any omitted field is left unchanged.",
    response_model=ApiResponse[OtherAssetRead],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Asset not found", error_payload="Asset not found"),
        500: INTERNAL_ERROR,
    },
)
def update_other_asset_endpoint(
    asset_id: str,
    payload: OtherAssetUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[OtherAssetRead]:
    row = update_other_asset(session, asset_id, payload)
    return ApiResponse(data=OtherAssetRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{asset_id}",
    summary="Delete asset category",
    description="Delete an asset category by id.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Asset not found", error_payload="Asset not found"),
        500: INTERNAL_ERROR,
    },
)
def delete_other_asset_endpoint(
    asset_id: str, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_other_asset(session, asset_id)
    return ApiResponse(data={"asset_id": asset_id})
