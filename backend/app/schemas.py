"""
Pydantic schemas for request/response validation
"""
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
import json

from .models import AppointmentStatus, PhotoSessionType, EquipmentType, UserRole, PackageStatus


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: str = Field(default="UTC", max_length=50)


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.CUSTOMER


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserPromoteToStudioOwner(BaseModel):
    """Schema for promoting user to studio owner"""
    confirm: bool = Field(..., description="Confirmation that user wants to become studio owner")


# Studio Schemas
class StudioBase(BaseModel):
    """Base studio schema"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, regex=r'^[a-z0-9-]+$')
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=500)
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # Settings
    timezone: str = Field(default="UTC", max_length=50)
    currency: str = Field(default="USD", max_length=3)
    booking_window_days: int = Field(default=30, ge=1, le=365)
    min_booking_notice_hours: int = Field(default=24, ge=0, le=168)


class StudioCreate(StudioBase):
    """Studio creation schema"""
    pass


class StudioUpdate(BaseModel):
    """Studio update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=500)
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # Settings
    timezone: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=3)
    booking_window_days: Optional[int] = Field(None, ge=1, le=365)
    min_booking_notice_hours: Optional[int] = Field(None, ge=0, le=168)


class StudioResponse(StudioBase):
    """Studio response schema"""
    id: UUID
    owner_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Package/Event Type Schemas
class CustomQuestion(BaseModel):
    """Custom question for booking form"""
    id: str
    question: str
    type: str = Field(..., regex=r'^(text|textarea|select|radio|checkbox|number|email|phone|date)$')
    required: bool = False
    options: Optional[List[str]] = None  # For select, radio, checkbox
    placeholder: Optional[str] = None
    help_text: Optional[str] = None


class PackageBase(BaseModel):
    """Base package schema"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, regex=r'^[a-z0-9-]+$')
    description: Optional[str] = None
    session_type: PhotoSessionType
    
    # Duration & Pricing
    duration_minutes: int = Field(..., ge=15, le=480)  # 15 minutes to 8 hours
    min_duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    max_duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    allow_custom_duration: bool = False
    
    # Pricing
    base_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    
    # Availability Settings
    buffer_time_before: int = Field(default=0, ge=0, le=120)  # Max 2 hours
    buffer_time_after: int = Field(default=0, ge=0, le=120)   # Max 2 hours
    
    # Booking Settings
    max_bookings_per_day: Optional[int] = Field(None, ge=1, le=50)
    min_booking_notice_hours: int = Field(default=24, ge=0, le=168)  # Max 1 week
    max_booking_days_ahead: int = Field(default=30, ge=1, le=365)    # Max 1 year
    
    # Requirements
    special_instructions: Optional[str] = None
    
    # Status & Visibility
    status: PackageStatus = PackageStatus.ACTIVE
    is_public: bool = True
    requires_approval: bool = False
    
    # SEO & Display
    featured_image_url: Optional[str] = Field(None, max_length=500)
    display_order: int = Field(default=0, ge=0)
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')  # Hex color
    
    @validator('min_duration_minutes')
    def validate_min_duration(cls, v, values):
        if v is not None and 'duration_minutes' in values:
            if v > values['duration_minutes']:
                raise ValueError('min_duration_minutes cannot be greater than duration_minutes')
        return v
    
    @validator('max_duration_minutes')
    def validate_max_duration(cls, v, values):
        if v is not None and 'duration_minutes' in values:
            if v < values['duration_minutes']:
                raise ValueError('max_duration_minutes cannot be less than duration_minutes')
        return v


class PackageCreate(PackageBase):
    """Package creation schema"""
    # Equipment (JSON strings)
    included_equipment: Optional[List[str]] = None  # List of equipment IDs
    optional_equipment: Optional[List[str]] = None  # List of equipment IDs
    
    # Custom Questions
    custom_questions: Optional[List[CustomQuestion]] = None
    
    @validator('included_equipment', 'optional_equipment', pre=True)
    def validate_equipment_lists(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Invalid JSON format for equipment list')
        return v


class PackageUpdate(BaseModel):
    """Package update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    session_type: Optional[PhotoSessionType] = None
    
    # Duration & Pricing
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    min_duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    max_duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    allow_custom_duration: Optional[bool] = None
    
    # Pricing
    base_price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    currency: Optional[str] = Field(None, max_length=3)
    
    # Availability Settings
    buffer_time_before: Optional[int] = Field(None, ge=0, le=120)
    buffer_time_after: Optional[int] = Field(None, ge=0, le=120)
    
    # Booking Settings
    max_bookings_per_day: Optional[int] = Field(None, ge=1, le=50)
    min_booking_notice_hours: Optional[int] = Field(None, ge=0, le=168)
    max_booking_days_ahead: Optional[int] = Field(None, ge=1, le=365)
    
    # Equipment & Requirements
    included_equipment: Optional[List[str]] = None
    optional_equipment: Optional[List[str]] = None
    special_instructions: Optional[str] = None
    
    # Custom Questions
    custom_questions: Optional[List[CustomQuestion]] = None
    
    # Status & Visibility
    status: Optional[PackageStatus] = None
    is_public: Optional[bool] = None
    requires_approval: Optional[bool] = None
    
    # SEO & Display
    featured_image_url: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = Field(None, ge=0)
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')


class PackageResponse(PackageBase):
    """Package response schema"""
    id: UUID
    studio_id: UUID
    
    # Equipment as parsed lists
    included_equipment: Optional[List[str]] = None
    optional_equipment: Optional[List[str]] = None
    
    # Custom Questions as parsed list
    custom_questions: Optional[List[CustomQuestion]] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        # Parse JSON fields
        data = {
            **obj.__dict__,
            'included_equipment': json.loads(obj.included_equipment) if obj.included_equipment else None,
            'optional_equipment': json.loads(obj.optional_equipment) if obj.optional_equipment else None,
            'custom_questions': json.loads(obj.custom_questions) if obj.custom_questions else None,
        }
        return cls(**data)


# TimeSlot Schemas
class TimeSlotBase(BaseModel):
    """Base time slot schema"""
    date: date
    start_time: time
    end_time: time
    max_capacity: int = Field(default=1, ge=1, le=10)
    is_available: bool = True
    override_price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)


class TimeSlotCreate(TimeSlotBase):
    """Time slot creation schema"""
    package_id: Optional[str] = None  # Optional: specific to package


class TimeSlotUpdate(BaseModel):
    """Time slot update schema"""
    max_capacity: Optional[int] = Field(None, ge=1, le=10)
    is_available: Optional[bool] = None
    override_price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)


class TimeSlotResponse(TimeSlotBase):
    """Time slot response schema"""
    id: UUID
    studio_id: UUID
    package_id: Optional[str]
    current_bookings: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Equipment Schemas
class EquipmentBase(BaseModel):
    """Base equipment schema"""
    name: str = Field(..., min_length=1, max_length=200)
    type: EquipmentType
    description: Optional[str] = None
    is_available: bool = True
    requires_supervision: bool = False
    additional_cost: Decimal = Field(default=0, ge=0, max_digits=10, decimal_places=2)


class EquipmentCreate(EquipmentBase):
    """Equipment creation schema"""
    studio_id: UUID


class EquipmentUpdate(BaseModel):
    """Equipment update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[EquipmentType] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None
    requires_supervision: Optional[bool] = None
    additional_cost: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)


class EquipmentResponse(EquipmentBase):
    """Equipment response schema"""
    id: UUID
    studio_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Appointment Schemas
class AppointmentBase(BaseModel):
    """Base appointment schema"""
    session_type: PhotoSessionType
    duration_minutes: int = Field(..., ge=15, le=480)
    equipment_requested: Optional[List[str]] = None  # Equipment IDs
    special_requirements: Optional[str] = None
    custom_form_responses: Optional[Dict[str, Any]] = None


class AppointmentCreate(AppointmentBase):
    """Appointment creation schema"""
    time_slot_id: UUID
    package_id: UUID
    
    @validator('equipment_requested', pre=True)
    def parse_equipment_list(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Invalid JSON format for equipment list')
        return v


class PublicAppointmentCreate(BaseModel):
    """Public appointment creation schema (for booking pages)"""
    # Customer info
    customer_email: EmailStr
    customer_first_name: str = Field(..., min_length=1, max_length=100)
    customer_last_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: Optional[str] = Field(None, max_length=20)
    
    # Appointment details
    package_id: UUID
    time_slot_id: UUID
    duration_minutes: Optional[int] = None  # Will default to package duration
    equipment_requested: Optional[List[str]] = None
    special_requirements: Optional[str] = None
    custom_form_responses: Optional[Dict[str, Any]] = None


class AppointmentUpdate(BaseModel):
    """Appointment update schema"""
    status: Optional[AppointmentStatus] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    equipment_requested: Optional[List[str]] = None
    special_requirements: Optional[str] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    """Appointment response schema"""
    id: UUID
    studio_id: UUID
    customer_id: UUID
    time_slot_id: UUID
    package_id: UUID
    
    base_price: Decimal
    equipment_cost: Decimal
    total_price: Decimal
    
    status: AppointmentStatus
    notes: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    
    # Relationships
    customer: UserResponse
    package: PackageResponse
    time_slot: TimeSlotResponse
    
    class Config:
        from_attributes = True


class AppointmentWithDetails(AppointmentResponse):
    """Appointment with full details"""
    studio: StudioResponse
    
    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token data for JWT"""
    user_id: Optional[str] = None


# API Response Schemas
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    status: str = "success"


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    status: str = "error"


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# Public API Schemas
class PublicStudioResponse(BaseModel):
    """Public studio info (limited fields)"""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    
    # Address
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    
    timezone: str
    currency: str
    booking_window_days: int
    min_booking_notice_hours: int
    
    class Config:
        from_attributes = True


class PublicPackageResponse(BaseModel):
    """Public package info for booking pages"""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    session_type: PhotoSessionType
    duration_minutes: int
    min_duration_minutes: Optional[int]
    max_duration_minutes: Optional[int]
    allow_custom_duration: bool
    base_price: Decimal
    currency: str
    featured_image_url: Optional[str]
    color: Optional[str]
    custom_questions: Optional[List[CustomQuestion]]
    
    class Config:
        from_attributes = True


class AvailableTimeSlot(BaseModel):
    """Available time slot for public booking"""
    id: UUID
    date: date
    start_time: time
    end_time: time
    available_capacity: int  # max_capacity - current_bookings
    price: Decimal  # Either package base_price or slot override_price
    
    class Config:
        from_attributes = True 