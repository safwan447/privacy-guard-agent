from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class PrivacyActionType(str, Enum):
    REDACT = "redact"  # Hide this segment
    KEEP = "keep"      # Leave this segment alone
    FINISH = "finish"  # Task complete

class PrivacyObservation(BaseModel):
    text_segment: str     # The current chunk of text
    context_before: str   # 50 characters of context before
    context_after: str    # 50 characters of context after
    segment_id: int       # Position in the document

class PrivacyAction(BaseModel):
    action: PrivacyActionType
    label: Optional[str] = "PII" # e.g., "NAME", "PHONE", "SSN"