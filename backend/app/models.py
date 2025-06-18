"""
Database models for the appointment system
"""
from datetime import datetime, time
from typing import Optional
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, 
    String, Text, Time, Date, Numeric, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid

from .database import Base


class AppointmentStatus(enum.Enum):
    """Appointment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class PhotoSessionType(enum.Enum):
    """Photo session type enumeration"""
    PORTRAIT = "portrait"
    FAMILY = "family"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    PRODUCT = "product"
    EVENT = "event"


class EquipmentType(enum.Enum):
    """Equipment type enumeration"""
    CAMERA = "camera"
    LIGHTING = "lighting"
    BACKDROP = "backdrop"
    PROPS = "props"


class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    STUDIO_OWNER = "studio_owner"
    STAFF = "staff"
    CUSTOMER = "customer"


class PackageStatus(enum.Enum):
    """Package status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class User(Base):
    """User model - handles both studio owners and customers"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth fields
    provider = Column(String(50), nullable=True)  # google, github, etc.
    provider_id = Column(String(255), nullable=True)
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Relationships
    owned_studios = relationship("Studio", back_populates="owner")
    appointments_as_customer = relationship("Appointment", foreign_keys="Appointment.customer_id", back_populates="customer")


class Studio(Base):
    """Studio model - for multi-tenant SaaS"""
    __tablename__ = "studios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)  # For custom URLs
    description = Column(Text, nullable=True)
    
    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Contact info
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    currency = Column(String(3), default="USD")
    booking_window_days = Column(Integer, default=30)  # How far ahead bookings allowed
    min_booking_notice_hours = Column(Integer, default=24)  # Minimum notice required
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_studios")
    time_slots = relationship("TimeSlot", back_populates="studio", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="studio", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="studio", cascade="all, delete-orphan")
    packages = relationship("Package", back_populates="studio", cascade="all, delete-orphan")


class Package(Base):
    """Package/Event Type model - Cal.com style service packages"""
    __tablename__ = "packages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    studio_id = Column(UUID(as_uuid=True), ForeignKey("studios.id"), nullable=False)
    
    # Basic Info
    name = Column(String(200), nullable=False)
    slug = Column(String(100), nullable=False)  # URL-friendly name
    description = Column(Text, nullable=True)
    session_type = Column(SQLEnum(PhotoSessionType), nullable=False)
    
    # Duration & Pricing
    duration_minutes = Column(Integer, nullable=False)  # Standard duration
    min_duration_minutes = Column(Integer, nullable=True)  # Minimum if flexible
    max_duration_minutes = Column(Integer, nullable=True)  # Maximum if flexible
    allow_custom_duration = Column(Boolean, default=False)
    
    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Availability Settings
    buffer_time_before = Column(Integer, default=0)  # Minutes before
    buffer_time_after = Column(Integer, default=0)   # Minutes after
    
    # Booking Settings
    max_bookings_per_day = Column(Integer, nullable=True)
    min_booking_notice_hours = Column(Integer, default=24)
    max_booking_days_ahead = Column(Integer, default=30)
    
    # Equipment & Requirements
    included_equipment = Column(Text, nullable=True)  # JSON string of included equipment
    optional_equipment = Column(Text, nullable=True)  # JSON string of optional equipment
    special_instructions = Column(Text, nullable=True)
    
    # Custom Questions for Booking Form
    custom_questions = Column(Text, nullable=True)  # JSON string of custom questions
    
    # Status & Visibility
    status = Column(SQLEnum(PackageStatus), default=PackageStatus.ACTIVE)
    is_public = Column(Boolean, default=True)  # Show on public booking page
    requires_approval = Column(Boolean, default=False)  # Manual approval required
    
    # SEO & Display
    featured_image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0)  # Order on booking page
    color = Column(String(7), nullable=True)  # Hex color for UI
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    studio = relationship("Studio", back_populates="packages")
    appointments = relationship("Appointment", back_populates="package")
    
    # Composite unique constraint
    __table_args__ = (
        {'extend_existing': True}
    )


class TimeSlot(Base):
    """Time slot model"""
    __tablename__ = "time_slots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    studio_id = Column(UUID(as_uuid=True), ForeignKey("studios.id"), nullable=False)
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"), nullable=True)  # Optional: specific to package
    
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    max_capacity = Column(Integer, default=1)
    current_bookings = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    
    # Override pricing for specific slots
    override_price = Column(Numeric(10, 2), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    studio = relationship("Studio", back_populates="time_slots")
    package = relationship("Package")
    appointments = relationship("Appointment", back_populates="time_slot")


class Equipment(Base):
    """Equipment model"""
    __tablename__ = "equipment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    studio_id = Column(UUID(as_uuid=True), ForeignKey("studios.id"), nullable=False)
    
    name = Column(String(200), nullable=False)
    type = Column(SQLEnum(EquipmentType), nullable=False)
    description = Column(Text, nullable=True)
    
    is_available = Column(Boolean, default=True)
    requires_supervision = Column(Boolean, default=False)
    additional_cost = Column(Numeric(10, 2), default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    studio = relationship("Studio", back_populates="equipment")


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    studio_id = Column(UUID(as_uuid=True), ForeignKey("studios.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    time_slot_id = Column(UUID(as_uuid=True), ForeignKey("time_slots.id"), nullable=False)
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"), nullable=False)  # Required now
    
    # Appointment details (can override package defaults)
    session_type = Column(SQLEnum(PhotoSessionType), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    equipment_requested = Column(String(1000), nullable=True)  # JSON string of equipment IDs
    special_requirements = Column(Text, nullable=True)
    
    # Custom form responses
    custom_form_responses = Column(Text, nullable=True)  # JSON string of responses
    
    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)
    equipment_cost = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Status
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Relationships
    studio = relationship("Studio", back_populates="appointments")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="appointments_as_customer")
    time_slot = relationship("TimeSlot", back_populates="appointments")
    package = relationship("Package", back_populates="appointments")


class EmailTemplate(Base):
    """Email template model for customizable notifications"""
    __tablename__ = "email_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    studio_id = Column(UUID(as_uuid=True), ForeignKey("studios.id"), nullable=False)
    
    name = Column(String(100), nullable=False)  # booking_confirmation, reminder, etc.
    subject = Column(String(200), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 