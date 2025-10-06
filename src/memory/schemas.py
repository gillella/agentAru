from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class MemoryEntry(BaseModel):
    """Structured memory entry"""

    id: str
    content: str
    memory_type: str  # episodic, semantic, procedural
    metadata: Dict[str, Any]
    timestamp: datetime
    relevance_score: float = 1.0
    decay_factor: float = 1.0


class MemorySearchResult(BaseModel):
    """Memory search result"""

    memory: str
    score: float
    metadata: Dict[str, Any] = {}
    id: Optional[str] = None
