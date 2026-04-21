import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Finding

logger = logging.getLogger(__name__)

VALID_SEVERITIES = {"Low", "Medium", "High", "Critical"}


def store_finding(finding: dict, db: Session | None = None) -> dict:
    owned = db is None
    if owned:
        db = SessionLocal()
    try:
        required = {"id", "topic", "severity", "summary"}
        missing = required - finding.keys()
        if missing:
            raise ValueError(f"Finding is missing required fields: {missing}")

        severity = finding["severity"].strip().title()
        if severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity '{severity}'. Must be one of {VALID_SEVERITIES}")

        existing = db.get(Finding, finding["id"])

        if existing:
            existing.topic = finding["topic"].strip().title()
            existing.severity = severity
            existing.summary = finding["summary"].strip()
            existing.stored_at = datetime.now(timezone.utc)
            logger.info("[STORE] Updated existing finding: %s", finding["id"])
        else:
            db.add(Finding(
                id=finding["id"],
                topic=finding["topic"].strip().title(),
                severity=severity,
                summary=finding["summary"].strip(),
            ))
            logger.info("[STORE] Saved new finding: %s", finding["id"])

        db.commit()
        return {"status": "stored", "id": finding["id"]}
    finally:
        if owned:
            db.close()


def get_all_findings(db: Session, severity: str | None = None, topic: str | None = None) -> list[Finding]:
    query = db.query(Finding)
    if severity:
        query = query.filter(Finding.severity == severity.strip().title())
    if topic:
        query = query.filter(Finding.topic.ilike(f"%{topic}%"))
    return query.order_by(Finding.stored_at.desc()).all()
