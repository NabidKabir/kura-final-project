# src/models/types.py - Core data types for the system

from typing import Dict, List, Optional, TypedDict, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class WasteType(str, Enum):
    """
    Enumeration of different waste types we can handle.
    This helps ensure consistency across the system.
    """
    E_WASTE = "e-waste"
    MEDICAL = "medical"
    HAZARDOUS = "hazardous"
    RECYCLABLE = "recyclable" 
    ORGANIC = "organic"
    HOUSEHOLD = "household"
    UNKNOWN = "unknown"

class HazardLevel(str, Enum):
    """Risk level of waste disposal"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ==========================================
# State Management for LangGraph
# ==========================================

class WasteManagementState(TypedDict):
    """
    State object that flows through our multi-agent workflow.
    This is the 'memory' that agents share and update as they work.
    """
    # User input
    user_query: str
    user_location: Optional[Dict[str, str]]
    
    # Classification results
    waste_type: Optional[str]
    waste_classification: Optional[Dict]
    
    # Regulatory information
    local_regulations: Optional[Dict]
    
    # Location data
    disposal_locations: Optional[List[Dict]]
    
    # Final output
    final_response: Optional[str]
    guidance_steps: Optional[List[str]]
    
    # Error handling
    error_message: Optional[str]
    
    # Processing metadata
    processing_step: Optional[str]
    confidence_score: Optional[float]

# ==========================================
# Pydantic Models for API and Data Validation
# ==========================================

class LocationModel(BaseModel):
    """User location information"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country: str = "US"

class WasteClassificationResult(BaseModel):
    """Result from waste classification"""
    primary_type: WasteType
    sub_type: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    hazard_level: HazardLevel
    special_handling: bool = False
    description: Optional[str] = None

class RegulationInfo(BaseModel):
    """Local waste disposal regulations"""
    jurisdiction: str  # State, city, or county
    waste_type: WasteType
    rules: str
    preparation_steps: List[str] = []
    restrictions: List[str] = []
    penalties: Optional[str] = None
    last_updated: datetime
    source_url: Optional[str] = None

class DisposalLocation(BaseModel):
    """Disposal facility information"""
    name: str
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    distance_km: Optional[float] = None
    accepted_waste_types: List[WasteType]
    hours: List[str] = []
    special_instructions: Optional[str] = None
    certification: Optional[str] = None
    rating: Optional[float] = Field(ge=0.0, le=5.0, default=None)

class UserQuery(BaseModel):
    """Incoming user query"""
    query: str = Field(min_length=1, max_length=1000)
    location: Optional[LocationModel] = None
    image_data: Optional[str] = None  # Base64 encoded image
    user_id: Optional[str] = None

class WasteManagementResponse(BaseModel):
    """Complete response to user"""
    waste_classification: WasteClassificationResult
    regulations: Optional[RegulationInfo] = None
    disposal_locations: List[DisposalLocation] = []
    guidance: str
    step_by_step_instructions: List[str] = []
    warnings: List[str] = []
    processing_time_ms: int
    confidence_score: float

# ==========================================
# Error Models
# ==========================================

class ErrorResponse(BaseModel):
    """Standardized error response"""
    error_type: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ==========================================
# Database Models (we'll use these later with SQLAlchemy)
# ==========================================

class BaseDBModel:
    """Base model with common fields for database models"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

print("✅ Data models and types defined successfully!")
print("📊 Available waste types:", [wt.value for wt in WasteType])
print("⚠️  Hazard levels:", [hl.value for hl in HazardLevel])