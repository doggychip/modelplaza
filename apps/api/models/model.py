import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Model(Base):
    __tablename__ = "models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    framework: Mapped[str | None] = mapped_column(String(50))
    task: Mapped[str | None] = mapped_column(String(50))
    license_type: Mapped[str | None] = mapped_column(String(50))
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    visibility: Mapped[str] = mapped_column(String(20), default="public")
    gitea_repo_id: Mapped[int | None] = mapped_column(Integer)
    total_downloads: Mapped[int] = mapped_column(BigInteger, default=0)
    total_likes: Mapped[int] = mapped_column(Integer, default=0)

    # On-chain provenance
    chain_tx_hash: Mapped[str | None] = mapped_column(String(66))
    chain_block_number: Mapped[int | None] = mapped_column(BigInteger)
    chain_contract_address: Mapped[str | None] = mapped_column(String(42))
    model_content_hash: Mapped[str | None] = mapped_column(String(66))
    provenance_registered_at: Mapped[datetime | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    versions: Mapped[list["ModelVersion"]] = relationship(back_populates="model", cascade="all, delete-orphan")

    __table_args__ = (
        # Each user can only have one model with a given slug
        {"sqlite_autoincrement": False},
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    commit_sha: Mapped[str | None] = mapped_column(String(40))
    content_hash: Mapped[str | None] = mapped_column(String(66))
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    chain_tx_hash: Mapped[str | None] = mapped_column(String(66))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    model: Mapped["Model"] = relationship(back_populates="versions")
