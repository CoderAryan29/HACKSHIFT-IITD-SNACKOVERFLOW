from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from agent_service.auth import AuthenticatedUser, get_current_user
from core_api.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


class ProfileSelection(BaseModel):
    role: Literal["farmer", "buyer"]


class QuestionnaireSubmission(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
    state: str | None = Field(default=None, max_length=120)
    district_name: str | None = Field(default=None, max_length=120)
    farm_size_acres: float | None = Field(default=None, ge=0, le=1_000_000)
    land_ownership: str | None = Field(default=None, max_length=40)
    crops: list[str] = Field(default_factory=list, max_length=30)
    buyer_interests: list[str] = Field(default_factory=list, max_length=30)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    clear_location: bool = False
    skipped: bool = False


@router.get("/profile")
def get_profile(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = db.execute(
        text(
            """
            SELECT uid, role, display_name, phone, state, district_name,
                   farm_size_acres, land_ownership, crops, buyer_interests,
                   lat, lng, onboarding_completed, questionnaire_completed
            FROM users
            WHERE uid = :uid
            """
        ),
        {"uid": user["uid"]},
    ).mappings().first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Choose a Farmer or Buyer role to finish setting up your account.",
        )
    return dict(profile)


@router.put("/profile")
def save_profile(
    selection: ProfileSelection,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not user["email"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Your Google account must provide an email address to create a KisanSetu profile.",
        )

    profile = db.execute(
        text(
            """
            INSERT INTO users (uid, email, display_name, role, onboarding_completed)
            VALUES (:uid, :email, :display_name, :role, FALSE)
            ON CONFLICT (uid) DO UPDATE SET
                email = EXCLUDED.email,
                display_name = COALESCE(EXCLUDED.display_name, users.display_name),
                role = EXCLUDED.role,
                updated_at = NOW()
            RETURNING uid, role, display_name, phone, state, district_name,
                      farm_size_acres, land_ownership, crops, buyer_interests,
                      lat, lng, onboarding_completed, questionnaire_completed
            """
        ),
        {
            "uid": user["uid"],
            "email": user["email"],
            "display_name": user["name"],
            "role": selection.role,
        },
    ).mappings().one()
    db.commit()
    return dict(profile)


@router.put("/questionnaire")
def save_questionnaire(
    submission: QuestionnaireSubmission,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not user["email"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Your Google account must provide an email address to save a KisanSetu profile.",
        )

    if not submission.skipped and (submission.lat is None) != (submission.lng is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Latitude and longitude must be submitted together.",
        )

    existing = db.execute(
        text("SELECT role FROM users WHERE uid = :uid"),
        {"uid": user["uid"]},
    ).mappings().first()
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Choose a Farmer or Buyer account type before completing the questionnaire.",
        )

    location_values = (
        not submission.skipped
        and not submission.clear_location
        and submission.lat is not None
    )
    profile = db.execute(
        text(
            """
            UPDATE users
            SET email = :email,
                display_name = CASE WHEN :skipped THEN display_name ELSE COALESCE(NULLIF(:display_name, ''), display_name) END,
                phone = CASE WHEN :skipped THEN phone ELSE COALESCE(NULLIF(:phone, ''), phone) END,
                state = CASE WHEN :skipped THEN state ELSE COALESCE(NULLIF(:state, ''), state) END,
                district_name = CASE WHEN :skipped THEN district_name ELSE COALESCE(NULLIF(:district_name, ''), district_name) END,
                farm_size_acres = CASE WHEN :skipped THEN farm_size_acres ELSE COALESCE(:farm_size_acres, farm_size_acres) END,
                land_ownership = CASE WHEN :skipped THEN land_ownership ELSE COALESCE(NULLIF(:land_ownership, ''), land_ownership) END,
                crops = CASE WHEN :skipped THEN crops ELSE :crops END,
                buyer_interests = CASE WHEN :skipped THEN buyer_interests ELSE :buyer_interests END,
                lat = CASE
                    WHEN :clear_location THEN NULL
                    WHEN :has_location THEN :lat
                    ELSE lat
                END,
                lng = CASE
                    WHEN :clear_location THEN NULL
                    WHEN :has_location THEN :lng
                    ELSE lng
                END,
                onboarding_completed = TRUE,
                questionnaire_completed = TRUE,
                updated_at = NOW()
            WHERE uid = :uid
            RETURNING uid, role, display_name, phone, state, district_name,
                      farm_size_acres, land_ownership, crops, buyer_interests,
                      lat, lng, onboarding_completed, questionnaire_completed
            """
        ),
        {
            "uid": user["uid"],
            "email": user["email"],
            "display_name": submission.display_name,
            "phone": submission.phone,
            "state": submission.state,
            "district_name": submission.district_name,
            "farm_size_acres": submission.farm_size_acres,
            "land_ownership": submission.land_ownership,
            "crops": submission.crops,
            "buyer_interests": submission.buyer_interests,
            "lat": submission.lat if location_values else None,
            "lng": submission.lng if location_values else None,
            "has_location": location_values,
            "clear_location": submission.clear_location,
            "skipped": submission.skipped,
        },
    ).mappings().one()
    db.commit()
    return dict(profile)