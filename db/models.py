from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from db.database import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    stored_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
