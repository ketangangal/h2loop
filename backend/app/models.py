from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class JobStatus:
    """
    Job status constants for tracking processing stages.
    Uses string literals for JSON serialization.
    Legacy aliases maintained for backward compatibility.
    """
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    GENERATING_FLOWCHART = "generating_flowchart"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    
    # Legacy aliases for compatibility
    QUEUED = "submitted"
    IN_PROGRESS = "processing"
    SUCCESS = "completed"


@dataclass
class FunctionResult:
    """
    Result of flowchart generation for a single function/code block.
    - validated: whether mmdc successfully parsed the Mermaid syntax.
    - error: optional error message if validation failed.
    """
    name: str
    mermaid: str
    validated: bool
    error: Optional[str] = None


@dataclass
class JobState:
    """
    Internal job state (in-memory store).
    Tracks status, original code, progress, and generated flowcharts.
    NOTE: Lost on restart; no persistence layer.
    """
    id: str
    code: str
    status: str = JobStatus.QUEUED
    total_functions: int = 0
    processed_functions: int = 0
    functions: List[FunctionResult] = field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class CreateJobRequest(BaseModel):
    """Request payload for creating a new job (POST /api/jobs)."""
    code: str


class FunctionResultResponse(BaseModel):
    name: str
    mermaid: str
    validated: bool
    error: Optional[str] = None


class JobSummaryResponse(BaseModel):
    """
    Job summary for list endpoints; uses camelCase aliases for frontend.
    Does not include code or full flowchart results.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: str
    total_functions: int = Field(0, alias="totalFunctions")
    processed_functions: int = Field(0, alias="processedFunctions")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")


class JobDetailResponse(JobSummaryResponse):
    """
    Full job detail including code and generated flowcharts.
    Used by GET /api/jobs/{id}.
    """
    code: str
    error: Optional[str] = None
    functions: List[FunctionResultResponse] = Field(default_factory=list)


def to_summary(job: JobState) -> JobSummaryResponse:
    """Convert internal JobState to API summary response."""
    return JobSummaryResponse(
        id=job.id,
        status=job.status,
        totalFunctions=job.total_functions,
        processedFunctions=job.processed_functions,
        createdAt=job.created_at,
        updatedAt=job.updated_at,
    )


def to_detail(job: JobState) -> JobDetailResponse:
    """Convert internal JobState to full API detail response."""
    return JobDetailResponse(
        **to_summary(job).model_dump(),
        code=job.code,
        error=job.error,
        functions=[
            FunctionResultResponse(**asdict(func)) for func in job.functions
        ],
    )

