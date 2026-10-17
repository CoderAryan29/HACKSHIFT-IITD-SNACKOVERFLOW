
from datetime import date
from decimal import Decimal
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Date,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for KisanSetu database models."""
    pass


class DocChunk(Base):
    """Maps to the existing public.doc_chunks table."""

    __tablename__ = "doc_chunks"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    crop_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    disease_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(768), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )


class District(Base):
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(Text, nullable=False)
    district: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    normal_rainfall_mm: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 1), nullable=True
    )
    default_soil: Mapped[str | None] = mapped_column(Text, nullable=True)


class Mandi(Base):
    __tablename__ = "mandis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(Text, nullable=False)
    district: Mapped[str] = mapped_column(Text, nullable=False)
    district_id: Mapped[int | None] = mapped_column(
        ForeignKey("districts.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    agmarknet_code: Mapped[str | None] = mapped_column(Text, nullable=True)


class MandiPrice(Base):
    __tablename__ = "mandi_prices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    mandi_id: Mapped[int] = mapped_column(
        ForeignKey("mandis.id"), nullable=False
    )
    commodity: Mapped[str] = mapped_column(Text, nullable=False)
    variety: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    max_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    modal_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    arrivals_qtl: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )


class PriceForecast(Base):
    __tablename__ = "price_forecasts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mandi_id: Mapped[int] = mapped_column(
        ForeignKey("mandis.id"), nullable=False
    )
    commodity: Mapped[str] = mapped_column(Text, nullable=False)
    issued_on: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    p10: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    p50: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    p90: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    model_version: Mapped[str | None] = mapped_column(Text, nullable=True)
