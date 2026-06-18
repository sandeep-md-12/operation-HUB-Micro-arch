import enum
from sqlalchemy import Column, String, Boolean, Enum
from app.utils.database import Base


class RoleEnum(str, enum.Enum):
    Admin = "Admin"
    Manager = "Manager"
    User = "User"


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.User, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __eq__(self, other):
        return isinstance(other, User) and self.user_id == other.user_id

    def __hash__(self):
        return hash(self.user_id)

    def __str__(self):
        return f"User({self.user_id}, {self.username}, {self.role})"

    def __repr__(self):
        return self.__str__()
