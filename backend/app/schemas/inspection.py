from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InspectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str | None
    image_filename: str
    image_path: str
    inspection_type: str
    result: str
    confidence: float
    analysis_metadata: str
    human_review_status: str
    created_at: datetime
