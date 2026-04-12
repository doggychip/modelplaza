import hashlib
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models.download import Download
from models.model import Model, ModelVersion
from models.user import User
from schemas import (
    ModelCreate,
    ModelListResponse,
    ModelResponse,
    ModelUpdate,
    ModelVersionResponse,
    ProvenanceResponse,
)
from services.chain import register_model_onchain
from services.gitea import create_gitea_repo
from services.storage import upload_to_minio

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    body: ModelCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check slug uniqueness for this user
    existing = await db.execute(
        select(Model).where(Model.owner_id == current_user.id, Model.slug == body.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Model slug already exists")

    # Create Gitea repo
    gitea_repo = await create_gitea_repo(current_user.username, body.slug)

    model = Model(
        owner_id=current_user.id,
        slug=body.slug,
        display_name=body.display_name or body.slug,
        description=body.description,
        framework=body.framework,
        task=body.task,
        license_type=body.license_type,
        tags=body.tags,
        visibility=body.visibility,
        gitea_repo_id=gitea_repo.get("id") if gitea_repo else None,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


@router.get("", response_model=ModelListResponse)
async def list_models(
    q: Optional[str] = Query(None, description="Search query"),
    framework: Optional[str] = Query(None),
    task: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Model).where(Model.visibility == "public")

    if q:
        query = query.where(
            Model.display_name.ilike(f"%{q}%") | Model.description.ilike(f"%{q}%")
        )
    if framework:
        query = query.where(Model.framework == framework)
    if task:
        query = query.where(Model.task == task)
    if tag:
        query = query.where(Model.tags.any(tag))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Model.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    models = list(result.scalars().all())

    return ModelListResponse(models=models, total=total, page=page, page_size=page_size)


@router.get("/{owner}/{slug}", response_model=ModelResponse)
async def get_model(owner: str, slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Model)
        .join(User, Model.owner_id == User.id)
        .where(User.username == owner, Model.slug == slug)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.patch("/{owner}/{slug}", response_model=ModelResponse)
async def update_model(
    owner: str,
    slug: str,
    body: ModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Model).where(Model.owner_id == current_user.id, Model.slug == slug)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(model, key, value)

    await db.commit()
    await db.refresh(model)
    return model


@router.delete("/{owner}/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    owner: str,
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Model).where(Model.owner_id == current_user.id, Model.slug == slug)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    await db.delete(model)
    await db.commit()


@router.post("/{owner}/{slug}/upload", response_model=ModelVersionResponse)
async def upload_model_files(
    owner: str,
    slug: str,
    file: UploadFile,
    version_tag: str = Query("v1"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Model).where(Model.owner_id == current_user.id, Model.slug == slug)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Read file and compute hash
    content = await file.read()
    content_hash = "0x" + hashlib.sha256(content).hexdigest()
    file_size = len(content)

    # Upload to MinIO
    object_key = f"{current_user.username}/{slug}/{version_tag}/{file.filename}"
    await upload_to_minio(object_key, content)

    # Create version record
    version = ModelVersion(
        model_id=model.id,
        version_tag=version_tag,
        content_hash=content_hash,
        file_size_bytes=file_size,
    )
    db.add(version)

    # Update model content hash
    model.model_content_hash = content_hash

    await db.commit()
    await db.refresh(version)

    # Register on-chain async (don't block the response)
    model_slug = f"{current_user.username}/{slug}"
    background_tasks.add_task(
        register_model_onchain, model.id, model_slug, content_hash, model.license_type or "unknown", db
    )

    return version


@router.get("/{owner}/{slug}/download")
async def download_model(
    owner: str,
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    result = await db.execute(
        select(Model)
        .join(User, Model.owner_id == User.id)
        .where(User.username == owner, Model.slug == slug)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Track download
    download = Download(
        model_id=model.id,
        user_id=current_user.id if current_user else None,
    )
    db.add(download)
    model.total_downloads += 1
    await db.commit()

    # Return presigned URL from MinIO
    from services.storage import get_download_url

    url = await get_download_url(f"{owner}/{slug}/")
    return {"download_url": url}


@router.get("/{owner}/{slug}/versions", response_model=list[ModelVersionResponse])
async def list_versions(
    owner: str,
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ModelVersion)
        .join(Model, ModelVersion.model_id == Model.id)
        .join(User, Model.owner_id == User.id)
        .where(User.username == owner, Model.slug == slug)
        .order_by(ModelVersion.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{owner}/{slug}/provenance", response_model=ProvenanceResponse)
async def get_provenance(owner: str, slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Model)
        .join(User, Model.owner_id == User.id)
        .where(User.username == owner, Model.slug == slug)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    explorer_url = None
    if model.chain_tx_hash:
        explorer_url = f"https://sepolia.basescan.org/tx/{model.chain_tx_hash}"

    return ProvenanceResponse(
        model_slug=f"{owner}/{slug}",
        content_hash=model.model_content_hash,
        chain_tx_hash=model.chain_tx_hash,
        chain_block_number=model.chain_block_number,
        chain_contract_address=model.chain_contract_address,
        license_type=model.license_type,
        registered_at=model.provenance_registered_at,
        explorer_url=explorer_url,
    )


@router.post("/{owner}/{slug}/like", status_code=status.HTTP_200_OK)
async def toggle_like(
    owner: str,
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Model)
        .join(User, Model.owner_id == User.id)
        .where(User.username == owner, Model.slug == slug)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Simple toggle (in production, use a separate likes table)
    model.total_likes += 1
    await db.commit()
    return {"likes": model.total_likes}
