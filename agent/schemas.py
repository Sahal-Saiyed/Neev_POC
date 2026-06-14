from typing import Optional, List, Literal
from pydantic import BaseModel, Field

RequestType = Literal [
    "formula_update",
    "new_shape",
    "formula_explanation"
]

RequestStatus = Literal[
    "pending",
    "approved",
    "rejected",
    "applied"
    ]

AgentIntent = Literal[
    "general",
    "formula_update",
    "new_shape",
    "formula_explanation",
    "unknown"
]

class FormulaUpdateData(BaseModel):
    project_id: Optional[str] = None
    project_name: Optional[str] = None

    category:str = "beam"

    shape_id: Optional[str] = None
    shape_name: Optional[str] = None

    output_name : Optional[str] = None
    current_formula : Optional[str] = None
    requested_formula : Optional[str] = None

    reason : Optional[str] = None

class NewShapeOutput(BaseModel):
    output_name: str
    formula: str
    unit: str = "m"

class NewShapeData(BaseModel):
    category: str = "beam"
    shape_name: Optional[str] = None
    description: Optional[str] = None
    outputs: List[NewShapeOutput] = Field(default_factory=list)
    reason: Optional[str] = None

class AgentResponse(BaseModel):
    intent: AgentIntent
    response_to_user: str
    missing_fields: List[str] = Field(default_factory=list)
    ready_to_submit: bool = False
    structured_data: dict = Field(default_factory=dict)

class ShapeOutputCreate(BaseModel):
    output_name: str
    formula: str
    unit: str = "m"

class NewShapePayload(BaseModel):
    shape_name: str
    description: Optional[str] = None
    image_path: Optional[str] = None
    outputs: List[ShapeOutputCreate] = Field(default_factory=list)

class AIRequestCreate(BaseModel):
    request_type: RequestType

    requested_by: str
    requested_by_name: str

    project_id: Optional[str] = None
    project_name: Optional[str] = None

    category: Optional[str] = None

    shape_id: Optional[str] = None
    shape_name: Optional[str] = None

    output_name: Optional[str] = None
    current_formula: Optional[str] = None
    requested_formula: Optional[str] = None

    reason: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_suggestion: Optional[str] = None

    new_shape_payload: Optional[NewShapePayload] = None
    new_shape_image_path: Optional[str] = None
    status: RequestStatus = "pending"