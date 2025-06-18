"""
Public API routes for customer bookings
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import json

from ..database import get_db
from ..models import (
    Studio, Package, TimeSlot, Appointment, User, Equipment,
    PackageStatus, AppointmentStatus, UserRole
)
from ..schemas import (
    PublicStudioResponse, PublicPackageResponse, AvailableTimeSlot,
    PublicAppointmentCreate, AppointmentResponse, MessageResponse
)
from ..services.auth import get_or_create_customer
from ..services.email import send_booking_confirmation, send_studio_notification

router = APIRouter()


@router.get("/studios/{studio_slug}", response_model=PublicStudioResponse)
async def get_studio_by_slug(
    studio_slug: str,
    db: Session = Depends(get_db)
):
    """
    Get studio information by slug for public booking pages
    
    This endpoint provides studio details needed for the booking page header
    and contact information.
    """
    studio = db.query(Studio).filter(
        and_(
            Studio.slug == studio_slug,
            Studio.is_active == True
        )
    ).first()
    
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Studio not found"
        )
    
    return PublicStudioResponse.from_attributes(studio)


@router.get("/studios/{studio_slug}/packages", response_model=List[PublicPackageResponse])
async def get_studio_packages(
    studio_slug: str,
    db: Session = Depends(get_db)
):
    """
    Get available packages/event types for a studio
    
    This endpoint shows all active, public packages that customers
    can book from the studio's booking page.
    """
    # Get studio by slug
    studio = db.query(Studio).filter(
        and_(
            Studio.slug == studio_slug,
            Studio.is_active == True
        )
    ).first()
    
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Studio not found"
        )
    
    # Get active, public packages
    packages = db.query(Package).filter(
        and_(
            Package.studio_id == studio.id,
            Package.status == PackageStatus.ACTIVE,
            Package.is_public == True
        )
    ).order_by(Package.display_order.asc(), Package.created_at.desc()).all()
    
    # Convert to public response format
    public_packages = []
    for package in packages:
        custom_questions = None
        if package.custom_questions:
            try:
                custom_questions = json.loads(package.custom_questions)
            except json.JSONDecodeError:
                custom_questions = None
        
        public_packages.append(PublicPackageResponse(
            id=str(package.id),
            name=package.name,
            slug=package.slug,
            description=package.description,
            session_type=package.session_type,
            duration_minutes=package.duration_minutes,
            min_duration_minutes=package.min_duration_minutes,
            max_duration_minutes=package.max_duration_minutes,
            allow_custom_duration=package.allow_custom_duration,
            base_price=package.base_price,
            currency=package.currency,
            featured_image_url=package.featured_image_url,
            color=package.color,
            custom_questions=custom_questions
        ))
    
    return public_packages


@router.get("/studios/{studio_id}/available-slots", response_model=List[AvailableTimeSlot])
async def get_available_time_slots(
    studio_id: str,
    package_id: Optional[str] = Query(None, description="Filter slots for specific package"),
    date_from: Optional[date] = Query(None, description="Start date for availability search"),
    date_to: Optional[date] = Query(None, description="End date for availability search"),
    db: Session = Depends(get_db)
):
    """
    Get available time slots for booking
    
    Returns time slots that have available capacity, considering:
    - Package-specific slots (if package_id provided)
    - Date range filtering
    - Current booking count vs max capacity
    - Package pricing (base price or slot override)
    """
    # Verify studio exists
    studio = db.query(Studio).filter(
        and_(
            Studio.id == studio_id,
            Studio.is_active == True
        )
    ).first()
    
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Studio not found"
        )
    
    # Set default date range if not provided
    if not date_from:
        date_from = date.today()
    
    if not date_to:
        date_to = date_from + timedelta(days=30)  # Default 30 days ahead
    
    # Build query for available slots
    query = db.query(TimeSlot).filter(
        and_(
            TimeSlot.studio_id == studio_id,
            TimeSlot.is_available == True,
            TimeSlot.date >= date_from,
            TimeSlot.date <= date_to,
            TimeSlot.current_bookings < TimeSlot.max_capacity
        )
    )
    
    # Filter by package if specified
    if package_id:
        # Verify package exists and is active
        package = db.query(Package).filter(
            and_(
                Package.id == package_id,
                Package.studio_id == studio_id,
                Package.status == PackageStatus.ACTIVE,
                Package.is_public == True
            )
        ).first()
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or not available"
            )
        
        # Include slots that are either general (package_id is None) or specific to this package
        query = query.filter(
            (TimeSlot.package_id == package_id) | (TimeSlot.package_id.is_(None))
        )
    
    # Order by date and time
    slots = query.order_by(TimeSlot.date.asc(), TimeSlot.start_time.asc()).all()
    
    # Convert to response format with pricing
    available_slots = []
    for slot in slots:
        # Determine price (slot override or package base price)
        price = slot.override_price
        
        if price is None and package_id:
            # Use package base price
            package = db.query(Package).filter(Package.id == package_id).first()
            if package:
                price = package.base_price
        
        if price is None:
            price = 0  # Fallback
        
        available_slots.append(AvailableTimeSlot(
            id=str(slot.id),
            date=slot.date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            available_capacity=slot.max_capacity - slot.current_bookings,
            price=price
        ))
    
    return available_slots


@router.post("/bookings", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_public_booking(
    booking_data: PublicAppointmentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new booking from the public booking page
    
    This endpoint handles the complete booking flow:
    1. Validates package and time slot availability
    2. Creates or finds customer account
    3. Creates appointment with proper pricing
    4. Sends confirmation emails
    5. Updates slot booking count
    """
    # Verify package exists and is bookable
    package = db.query(Package).filter(
        and_(
            Package.id == booking_data.package_id,
            Package.status == PackageStatus.ACTIVE,
            Package.is_public == True
        )
    ).first()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found or not available for booking"
        )
    
    # Verify time slot is available
    time_slot = db.query(TimeSlot).filter(
        and_(
            TimeSlot.id == booking_data.time_slot_id,
            TimeSlot.studio_id == package.studio_id,
            TimeSlot.is_available == True,
            TimeSlot.current_bookings < TimeSlot.max_capacity,
            TimeSlot.date >= date.today()  # Can't book past dates
        )
    ).first()
    
    if not time_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot not available or fully booked"
        )
    
    # Check if slot is specific to this package or general
    if time_slot.package_id and str(time_slot.package_id) != str(booking_data.package_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This time slot is not available for the selected package"
        )
    
    # Get or create customer
    customer = await get_or_create_customer(
        db=db,
        email=booking_data.customer_email,
        first_name=booking_data.customer_first_name,
        last_name=booking_data.customer_last_name,
        phone=booking_data.customer_phone
    )
    
    # Determine appointment duration
    duration = booking_data.duration_minutes or package.duration_minutes
    
    # Validate custom duration if provided
    if booking_data.duration_minutes and not package.allow_custom_duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom duration not allowed for this package"
        )
    
    if booking_data.duration_minutes:
        if package.min_duration_minutes and duration < package.min_duration_minutes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum duration is {package.min_duration_minutes} minutes"
            )
        
        if package.max_duration_minutes and duration > package.max_duration_minutes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum duration is {package.max_duration_minutes} minutes"
            )
    
    # Calculate pricing
    base_price = time_slot.override_price or package.base_price
    equipment_cost = 0  # TODO: Calculate based on requested equipment
    total_price = base_price + equipment_cost
    
    # Create appointment
    appointment = Appointment(
        id=str(uuid.uuid4()),
        studio_id=package.studio_id,
        customer_id=customer.id,
        time_slot_id=time_slot.id,
        package_id=package.id,
        session_type=package.session_type,
        duration_minutes=duration,
        equipment_requested=json.dumps(booking_data.equipment_requested) if booking_data.equipment_requested else None,
        special_requirements=booking_data.special_requirements,
        custom_form_responses=json.dumps(booking_data.custom_form_responses) if booking_data.custom_form_responses else None,
        base_price=base_price,
        equipment_cost=equipment_cost,
        total_price=total_price,
        status=AppointmentStatus.CONFIRMED if not package.requires_approval else AppointmentStatus.PENDING
    )
    
    # Update slot booking count
    time_slot.current_bookings += 1
    
    # Save to database
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Send confirmation emails
    try:
        # Get studio for email context
        studio = db.query(Studio).filter(Studio.id == package.studio_id).first()
        
        await send_booking_confirmation(
            db=db,
            appointment=appointment,
            customer=customer,
            studio=studio,
            package=package
        )
        
        await send_studio_notification(
            db=db,
            appointment=appointment,
            customer=customer,
            studio=studio,
            package=package
        )
    except Exception as e:
        # Log email error but don't fail the booking
        print(f"Email sending failed: {e}")
    
    # Load relationships for response
    appointment.customer = customer
    appointment.package = package
    appointment.time_slot = time_slot
    
    return AppointmentResponse.from_attributes(appointment)


@router.get("/bookings/{booking_id}", response_model=AppointmentResponse)
async def get_public_booking(
    booking_id: str,
    customer_email: str = Query(..., description="Customer email for verification"),
    db: Session = Depends(get_db)
):
    """
    Get booking details for customers
    
    Allows customers to view their booking details using booking ID
    and email verification.
    """
    # Find appointment
    appointment = db.query(Appointment).filter(Appointment.id == booking_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify customer email
    customer = db.query(User).filter(User.id == appointment.customer_id).first()
    
    if not customer or customer.email.lower() != customer_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid booking ID or email"
        )
    
    # Load relationships
    appointment.customer = customer
    appointment.package = db.query(Package).filter(Package.id == appointment.package_id).first()
    appointment.time_slot = db.query(TimeSlot).filter(TimeSlot.id == appointment.time_slot_id).first()
    
    return AppointmentResponse.from_attributes(appointment)


@router.post("/bookings/{booking_id}/cancel", response_model=MessageResponse)
async def cancel_public_booking(
    booking_id: str,
    customer_email: str = Query(..., description="Customer email for verification"),
    cancellation_reason: Optional[str] = Query(None, description="Reason for cancellation"),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking (customer self-service)
    
    Allows customers to cancel their own bookings using booking ID
    and email verification.
    """
    # Find appointment
    appointment = db.query(Appointment).filter(Appointment.id == booking_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify customer email
    customer = db.query(User).filter(User.id == appointment.customer_id).first()
    
    if not customer or customer.email.lower() != customer_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid booking ID or email"
        )
    
    # Check if already cancelled
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    # Check if completed
    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed booking"
        )
    
    # Update appointment status
    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_at = datetime.utcnow()
    appointment.cancellation_reason = cancellation_reason
    
    # Update time slot availability
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == appointment.time_slot_id).first()
    if time_slot:
        time_slot.current_bookings = max(0, time_slot.current_bookings - 1)
    
    db.commit()
    
    # TODO: Send cancellation confirmation email
    
    return MessageResponse(
        message="Booking cancelled successfully",
        status="success"
    ) 