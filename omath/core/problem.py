from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid


@dataclass
class Problem:
    id: str
    text: str
    kind: str  # e.g., "equation", "integral", "simplify", "prime", "logic"
    variables: List[str] = field(default_factory=list)
    domain: Optional[str] = None  # e.g., "int", "real"
    metadata: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def create(text: str, kind: str, variables: Optional[List[str]] = None, domain: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> "Problem":
        return Problem(
            id=str(uuid.uuid4()),
            text=text,
            kind=kind,
            variables=variables or [],
            domain=domain,
            metadata=metadata or {},
        )