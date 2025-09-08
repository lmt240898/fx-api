from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class AIProviderConfig(BaseModel):
    order: Optional[List[str]] = None
    sort: Optional[str] = None

class AIStrategy(BaseModel):
    model: str
    provider: Optional[AIProviderConfig] = None
    capabilities: Optional[Dict[str, bool]] = None

class AIConfig(BaseModel):
    strategies: Dict[str, AIStrategy]
    use_model: str
