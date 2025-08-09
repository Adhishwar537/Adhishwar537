from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Result:
    success: bool
    summary: str
    data: Dict[str, Any] = field(default_factory=dict)