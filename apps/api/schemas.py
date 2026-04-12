import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


# Auth
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None
    token_balance: int
    reputation_score: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Models
class ModelCreate(BaseModel):
    slug: str
    display_name: str | None = None
    description: str | None = None
    framework: str | None = None
    task: str | None = None
    license_type: str | None = None
    tags: list[str] | None = None
    visibility: str = "public"


class ModelUpdate(BaseModel):
    display_name: str | None = None
    description: str | None = None
    framework: str | None = None
    task: str | None = None
    license_type: str | None = None
    tags: list[str] | None = None
    visibility: str | None = None


class ModelResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    slug: str
    display_name: str | None
    description: str | None
    framework: str | None
    task: str | None
    license_type: str | None
    tags: list[str] | None
    visibility: str
    total_downloads: int
    total_likes: int
    chain_tx_hash: str | None
    model_content_hash: str | None
    provenance_registered_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ModelVersionResponse(BaseModel):
    id: uuid.UUID
    model_id: uuid.UUID
    version_tag: str
    commit_sha: str | None
    content_hash: str | None
    file_size_bytes: int | None
    chain_tx_hash: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProvenanceResponse(BaseModel):
    model_slug: str
    content_hash: str | None
    chain_tx_hash: str | None
    chain_block_number: int | None
    chain_contract_address: str | None
    license_type: str | None
    registered_at: datetime | None
    explorer_url: str | None


class ModelListResponse(BaseModel):
    models: list[ModelResponse]
    total: int
    page: int
    page_size: int
