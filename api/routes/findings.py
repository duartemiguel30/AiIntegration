from datetime import timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from api.limiter import limiter
from db.database import get_db
from db.models import Finding
from services.storage import get_all_findings

router = APIRouter(prefix="/findings", tags=["findings"])


def _serialize(f: Finding) -> dict:
    return {
        "id": f.id,
        "topic": f.topic,
        "severity": f.severity,
        "summary": f.summary,
        "stored_at": f.stored_at.replace(tzinfo=timezone.utc).isoformat(),
    }


@router.get("/")
@limiter.limit("60/minute")
def list_findings(
    request: Request,
    severity: str | None = Query(None, description="Filter by severity: Low, Medium, High, Critical"),
    topic: str | None = Query(None, description="Filter by topic (partial match)"),
    db: Session = Depends(get_db),
):
    findings = get_all_findings(db, severity=severity, topic=topic)
    return [_serialize(f) for f in findings]


@router.get("/{finding_id}")
@limiter.limit("60/minute")
def get_finding(request: Request, finding_id: str, db: Session = Depends(get_db)):
    finding = db.get(Finding, finding_id.upper())
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return _serialize(finding)
