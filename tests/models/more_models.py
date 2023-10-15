from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from tests.models.base import Base


class Pokemon(Base):
    __tablename__ = "pokemon"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    
    def __repr__(self) -> str:
        return f"Pokemon(id={self.id!r}, name={self.name!r})"
