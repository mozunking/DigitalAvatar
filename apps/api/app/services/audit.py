import hashlib
import json
from datetime import datetime

from app.models.models import AuditLog


class AuditService:
    @staticmethod
    def append(
        db,
        *,
        trace_id: str,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        result: str,
        request_summary: str = "",
        policy_hits: list[str] | None = None,
    ) -> AuditLog:
        last = db.query(AuditLog).order_by(AuditLog.created_at.desc()).first()
        hash_prev = last.hash_self if last else None
        payload = json.dumps(
            {
                "trace_id": trace_id,
                "actor": actor,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "result": result,
                "request_summary": request_summary,
                "policy_hits": policy_hits or [],
                "hash_prev": hash_prev,
                "timestamp": datetime.utcnow().isoformat(),
            },
            sort_keys=True,
        )
        hash_self = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        log = AuditLog(
            trace_id=trace_id,
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            request_summary=request_summary,
            policy_hits=json.dumps(policy_hits or []),
            hash_prev=hash_prev,
            hash_self=hash_self,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
