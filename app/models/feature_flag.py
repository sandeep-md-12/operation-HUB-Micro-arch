from sqlalchemy import Column, String, Boolean
from app.utils.database import Base


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    name = Column(String, primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)

    def __eq__(self, other):
        return isinstance(other, FeatureFlag) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"FeatureFlag({self.name}, enabled={self.enabled})"

    def __repr__(self):
        return self.__str__()
