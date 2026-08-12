import json
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    severity: str
    action: str
    actor_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

class PaginatedAuditLogsResponse(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: List[AuditLogResponse]
