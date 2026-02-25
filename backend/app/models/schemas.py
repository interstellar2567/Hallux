"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VerificationStatus(str, Enum):
    """Citation verification status"""
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    FAKE = "fake"
    URL_BROKEN = "url_broken"
    UNKNOWN = "unknown"


class LayerStatus(str, Enum):
    """Verification layer status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class VerificationOptions(BaseModel):
    """Options for citation verification"""
    enable_ai_scoring: bool = True
    check_content: bool = True
    enable_citation_graph: bool = True
    use_cache: bool = True
    timeout_seconds: int = 30


class CitationInput(BaseModel):
    """Single citation input"""
    citation: str = Field(..., description="Citation text to verify")
    context: Optional[str] = Field(None, description="Context surrounding the citation")
    options: Optional[VerificationOptions] = VerificationOptions()


class TextInput(BaseModel):
    """Full text input with multiple citations"""
    text: str = Field(..., description="Full text containing citations")
    format: str = Field("plain", description="Text format: plain, markdown, html")
    options: Optional[VerificationOptions] = VerificationOptions()


class BatchInput(BaseModel):
    """Batch citation verification input"""
    citations: List[str] = Field(..., description="List of citations to verify")
    priority: str = Field("balanced", description="Priority: speed, accuracy, balanced")
    options: Optional[VerificationOptions] = VerificationOptions()


class LayerResult(BaseModel):
    """Result from a single verification layer"""
    status: LayerStatus
    details: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class VerificationLayers(BaseModel):
    """Results from all verification layers"""
    url_validation: LayerResult
    metadata_check: LayerResult
    content_verification: LayerResult
    ai_scoring: LayerResult
    citation_graph: Optional[LayerResult] = None


class CitationSuggestion(BaseModel):
    """Suggested alternative citation"""
    title: str
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    confidence: float
    reason: str


class VerificationResult(BaseModel):
    """Citation verification result"""
    citation: str
    status: VerificationStatus
    confidence: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    verification_layers: VerificationLayers
    ai_reasoning: Optional[str] = None
    suggestions: Optional[List[CitationSuggestion]] = []
    metadata: Dict[str, Any] = {
        "processing_time_ms": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


class TextVerificationResult(BaseModel):
    """Full text verification result"""
    total_citations: int
    verified_count: int
    suspicious_count: int
    fake_count: int
    results: List[VerificationResult]
    overall_confidence: float
    processing_time_ms: int
    timestamp: str = datetime.utcnow().isoformat()


class BatchVerificationResult(BaseModel):
    """Batch verification result"""
    total_citations: int
    completed: int
    failed: int
    results: List[VerificationResult]
    processing_time_ms: int
    timestamp: str = datetime.utcnow().isoformat()


class ErrorResponse(BaseModel):
    """Error response model"""
    error: bool = True
    status_code: int
    message: str
    details: Optional[Dict[str, Any]] = None
