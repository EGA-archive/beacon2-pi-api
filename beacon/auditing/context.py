from datetime import datetime, timezone
from uuid import uuid4

from beacon.auditing.models import AuditModel


class AuditContext:

    def __init__(self, request_id: str):
        self.data = AuditModel(
            audit_schema_version="1.0.0",
            audit_id=str(uuid4()),
            request_id=request_id,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            duration_ms=None,

            request={...},
            identity={...},
            authorization={...},
            configuration={...},
            budget={...},
            database={...},
            execution={...},
            response={...},
            error=None,
            runtime={...},
            integrity={
                "persistence_status": "pending",
                "record_hash": None,
                "previous_record_hash": None
            }
        )

    def update_request(self, **kwargs):
        ...

    def update_identity(self, **kwargs):
        ...

    def update_authorization(self, **kwargs):
        ...

    def add_execution_event(self, **kwargs):
        ...

    def update_database(self, **kwargs):
        ...

    def update_response(self, **kwargs):
        ...

    def set_error(self, **kwargs):
        ...

    def finalize(self, status: str):
        ...

    def serialize(self):
        return self.data.model_dump(mode="json")