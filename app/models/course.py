from sqlalchemy import String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # collège / lycée / bac / etc.

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False
    )

    price_eur: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
