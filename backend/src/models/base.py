from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, class_mapper

from src.models.mixins.timing import TimingMixin


class Base(DeclarativeBase, TimingMixin):
    __abstract__ = True

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    repr_exclude_cols = (
        "created_at",
        "updated_at",
    )

    def to_dict(self) -> dict:
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}

    def __repr__(self) -> str:
        cols = []
        for key, value in self.to_dict().items():
            if key not in self.repr_exclude_cols:
                cols.append(f"{key}={value!r}")
        return f"{self.__class__.__name__}({', '.join(cols)})"
