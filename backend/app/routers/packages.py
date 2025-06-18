"""
Packages/Event Types API routes - Cal.com style service packages
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import json
import uuid

from ..database import get_db
from ..models import Package, Studio, User, UserRole, PackageStatus
from ..schemas import (
    PackageCreate, PackageUpdate, PackageResponse, PublicPackageResponse,
    MessageResponse, PaginatedResponse
)
from ..services.auth import get_current_user, require_studio_owner

router = APIRouter()


def get_user_studio_or_404(db: Session, user: User, studio_id: str) -> Studio:
    """Get studio that belongs to the current user or raise 404"""
    studio = db.query(Studio).filter(
        and_(
            Studio.id == studio_id,
            Studio.owner_id == user.id,
            Studio.is_active == True
        )
    ).first()
    
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Studio not found or access denied"
        )
    
    return studio


def get_package_or_404(db: Session, package_id: str, studio_id: str = None) -> Package:
    """Get package by ID, optionally filter by studio"""
    query = db.query(Package).filter(Package.id == package_id)
    
    if studio_id:
        query = query.filter(Package.studio_id == studio_id)
    
    package = query.first()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    return package


@router.post("/", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_package(
    package_data: PackageCreate,
    studio_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_studio_owner)
):
    """
    Create a new service package/event type for a studio
    
    This is similar to Cal.com's Event Types - it defines:
    - Service details (name, description, duration)
    - Pricing and availability settings
    - Custom booking questions
    - Equipment requirements
    """
    # Verify studio ownership
    studio = get_user_studio_or_404(db, current_user, studio_id)
    
    # Check if slug is unique within the studio
    existing_package = db.query(Package).filter(
        and_(
            Package.studio_id == studio_id,
            Package.slug == package_data.slug
        )
    ).first()
    
    if existing_package:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A package with this slug already exists in your studio"
        )
    
    # Convert lists to JSON strings for storage
    included_equipment_json = json.dumps(package_data.included_equipment) if package_data.included_equipment else None
    optional_equipment_json = json.dumps(package_data.optional_equipment) if package_data.optional_equipment else None
    custom_questions_json = json.dumps([q.dict() for q in package_data.custom_questions]) if package_data.custom_questions else None
    
    # Create package
    package = Package(
        id=uuid.uuid4(),
        studio_id=studio_id,
        name=package_data.name,
        slug=package_data.slug.lower(),
        description=package_data.description,
        session_type=package_data.session_type,
        duration_minutes=package_data.duration_minutes,
        min_duration_minutes=package_data.min_duration_minutes,
        max_duration_minutes=package_data.max_duration_minutes,
        allow_custom_duration=package_data.allow_custom_duration,
        base_price=package_data.base_price,
        currency=package_data.currency,
        buffer_time_before=package_data.buffer_time_before,
        buffer_time_after=package_data.buffer_time_after,
        max_bookings_per_day=package_data.max_bookings_per_day,
        min_booking_notice_hours=package_data.min_booking_notice_hours,
        max_booking_days_ahead=package_data.max_booking_days_ahead,
        included_equipment=included_equipment_json,
        optional_equipment=optional_equipment_json,
        special_instructions=package_data.special_instructions,
        custom_questions=custom_questions_json,
        status=package_data.status,
        is_public=package_data.is_public,
        requires_approval=package_data.requires_approval,
        featured_image_url=package_data.featured_image_url,
        display_order=package_data.display_order,
        color=package_data.color
    )
    
    db.add(package)
    db.commit()
    db.refresh(package)
    
    return PackageResponse.from_orm(package)


@router.get("/studio/{studio_id}", response_model=List[PackageResponse])
async def get_studio_packages(
    studio_id: str,
    status_filter: Optional[PackageStatus] = Query(None, description="Filter by package status"),
    is_public: Optional[bool] = Query(None, description="Filter by public visibility"),
    skip: int = Query(0, ge=0, description="Number of packages to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of packages to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_studio_owner)
):
    """
    Get all packages for a studio (studio owner only)
    
    Returns all packages with full details including custom questions
    and equipment lists for management purposes.
    """
    # Verify studio ownership
    studio = get_user_studio_or_404(db, current_user, studio_id)
    
    # Build query
    query = db.query(Package).filter(Package.studio_id == studio_id)
    
    if status_filter:
        query = query.filter(Package.status == status_filter)
    
    if is_public is not None:
        query = query.filter(Package.is_public == is_public)
    
    # Order by display order, then creation date
    query = query.order_by(Package.display_order.asc(), Package.created_at.desc())
    
    # Apply pagination
    packages = query.offset(skip).limit(limit).all()
    
    return [PackageResponse.from_orm(package) for package in packages]


@router.get("/{package_id}", response_model=PackageResponse)
async def get_package(
    package_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_studio_owner)
):
    """
    Get a specific package by ID (studio owner only)
    
    Returns full package details including custom questions and equipment lists.
    """
    package = get_package_or_404(db, package_id)
    
    # Verify studio ownership
    get_user_studio_or_404(db, current_user, str(package.studio_id))
    
    return PackageResponse.from_orm(package)


@router.put("/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: str,
    package_update: PackageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_studio_owner)
):
    """
    Update a package/event type
    
    Allows updating all package properties including pricing,
    duration, custom questions, and equipment requirements.
    """
    package = get_package_or_404(db, package_id)
    
    # Verify studio ownership
    get_user_studio_or_404(db, current_user, str(package.studio_id))
    
    # Update fields
    update_data = package_update.dict(exclude_unset=True)
    
    # Handle special fields that need JSON conversion
    if 'included_equipment' in update_data:
        update_data['included_equipment'] = json.dumps(update_data['included_equipment']) if update_data['included_equipment'] else None
    
    if 'optional_equipment' in update_data:
        update_data['optional_equipment'] = json.dumps(update_data['optional_equipment']) if update_data['optional_equipment'] else None
    
    if 'custom_questions' in update_data:
        if update_data['custom_questions']:
            update_data['custom_questions'] = json.dumps([q.dict() if hasattr(q, 'dict') else q for q in update_data['custom_questions']])
        else:
            update_data['custom_questions'] = None
    
    # Apply updates
    for field, value in update_data.items():
        setattr(package, field, value)
    
    package.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(package)
    
    return PackageResponse.from_orm(package)


@router.delete("/{package_id}", response_model=MessageResponse)
async def delete_package(
    package_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_studio_owner)
):
    """
    Delete a package/event type
    
    Note: This will fail if there are existing appointments
    linked to this package. Consider setting status to 'inactive' instead.
    """
    package = get_package_or_404(db, package_id)
    
    # Verify studio ownership
    get_user_studio_or_404(db, current_user, str(package.studio_id))
    
    # Check for existing appointments
    from ..models import Appointment
    appointment_count = db.query(Appointment).filter(Appointment.package_id == package_id).count()
    
    if appointment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete package with {appointment_count} existing appointments. Set status to 'inactive' instead."
        )
    
    db.delete(package)
    db.commit()
    
    return MessageResponse(
        message="Package deleted successfully",
        status="success"
    )


@router.post("/{package_id}/duplicate", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_package(
    package_id: str,
    new_name: Optional[str] = Query(None, description="Name for the duplicated package"),
    new_slug: Optional[str] = Query(None, description="Slug for the duplicated package"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_studio_owner)  
):
    """
    Duplicate an existing package
    
    Creates a copy of the package with a new name and slug.
    Useful for creating variations of existing packages.
    """
    original_package = get_package_or_404(db, package_id)
    
    # Verify studio ownership
    get_user_studio_or_404(db, current_user, str(original_package.studio_id))
    
    # Generate new name and slug if not provided
    if not new_name:
        new_name = f"{original_package.name} (Copy)"
    
    if not new_slug:
        new_slug = f"{original_package.slug}-copy"
    else:
        new_slug = new_slug.lower()
    
    # Check if new slug is unique
    existing_package = db.query(Package).filter(
        and_(
            Package.studio_id == original_package.studio_id,
            Package.slug == new_slug
        )
    ).first()
    
    if existing_package:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A package with this slug already exists in your studio"
        )
    
    # Create duplicate
    duplicate_package = Package(
        id=uuid.uuid4(),
        studio_id=original_package.studio_id,
        name=new_name,
        slug=new_slug,
        description=original_package.description,
        session_type=original_package.session_type,
        duration_minutes=original_package.duration_minutes,
        min_duration_minutes=original_package.min_duration_minutes,
        max_duration_minutes=original_package.max_duration_minutes,
        allow_custom_duration=original_package.allow_custom_duration,
        base_price=original_package.base_price,
        currency=original_package.currency,
        buffer_time_before=original_package.buffer_time_before,
        buffer_time_after=original_package.buffer_time_after,
        max_bookings_per_day=original_package.max_bookings_per_day,
        min_booking_notice_hours=original_package.min_booking_notice_hours,
        max_booking_days_ahead=original_package.max_booking_days_ahead,
        included_equipment=original_package.included_equipment,
        optional_equipment=original_package.optional_equipment,
        special_instructions=original_package.special_instructions,
        custom_questions=original_package.custom_questions,
        status=PackageStatus.DRAFT,  # New packages start as draft
        is_public=False,  # New packages start as private
        requires_approval=original_package.requires_approval,
        featured_image_url=original_package.featured_image_url,
        display_order=original_package.display_order,
        color=original_package.color
    )
    
    db.add(duplicate_package)
    db.commit()
    db.refresh(duplicate_package)
    
    return PackageResponse.from_orm(duplicate_package)


# ============================================================================
# PUBLIC API ENDPOINTS (for booking pages) 
# ============================================================================

@router.get("/public/studio/{studio_slug}", response_model=List[PublicPackageResponse])
async def get_public_studio_packages(
    studio_slug: str,
    db: Session = Depends(get_db)
):
    """
    Get public packages for a studio by slug (public endpoint)
    
    This endpoint is used by the public booking pages to show
    available service packages to customers.
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


@router.get("/public/{package_id}", response_model=PublicPackageResponse)
async def get_public_package(
    package_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific public package by ID (public endpoint)
    
    Used by booking forms to get package details including
    custom questions and pricing information.
    """
    package = db.query(Package).filter(
        and_(
            Package.id == package_id,
            Package.status == PackageStatus.ACTIVE,
            Package.is_public == True
        )
    ).first()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found or not available for booking"
        )
    
    # Parse custom questions
    custom_questions = None
    if package.custom_questions:
        try:
            custom_questions = json.loads(package.custom_questions)
        except json.JSONDecodeError:
            custom_questions = None
    
    return PublicPackageResponse(
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
    ) 