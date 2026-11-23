import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models.profile import TestParameter, TestProfile
from app.database.models.audit import AuditEvent
from app.schemas.profile import TestProfileCreate, TestProfileUpdate


class ProfileNotFoundError(Exception):
    pass


def create_profile(db: Session, payload: TestProfileCreate) -> TestProfile:
    profile = TestProfile(
        name=payload.name,
        device_type=payload.device_type,
        description=payload.description,
        is_active=payload.is_active,
        created_by=payload.created_by,
        version=1,
    )
    profile.parameters = [
        TestParameter(**parameter.model_dump())
        for parameter in payload.parameters
    ]
    db.add(profile)
    db.flush()
    db.add(AuditEvent(
        entity_type="TestProfile",
        entity_id=profile.id,
        action="CREATE",
        actor=payload.created_by,
        details_json=json.dumps({"name": profile.name, "version": profile.version}),
    ))
    db.commit()
    db.refresh(profile)
    return profile


def list_profiles(
    db: Session,
    device_type: str | None = None,
) -> list[TestProfile]:
    statement = (
        select(TestProfile)
        .options(selectinload(TestProfile.parameters))
        .order_by(TestProfile.created_at.desc())
    )
    if device_type:
        statement = statement.where(TestProfile.device_type == device_type)
    return list(db.scalars(statement).unique().all())


def get_profile(db: Session, profile_id: str) -> TestProfile:
    profile = db.scalar(
        select(TestProfile)
        .options(selectinload(TestProfile.parameters))
        .where(TestProfile.id == profile_id)
    )
    if not profile:
        raise ProfileNotFoundError("Test profile not found")
    return profile


def update_profile(
    db: Session,
    profile_id: str,
    payload: TestProfileUpdate,
) -> TestProfile:
    profile = get_profile(db, profile_id)
    updates = payload.model_dump(exclude_unset=True)
    parameters = updates.pop("parameters", None)

    for field, value in updates.items():
        setattr(profile, field, value)

    if parameters is not None:
        profile.parameters = [
            TestParameter(**parameter)
            for parameter in parameters
        ]

    profile.version += 1
    db.add(AuditEvent(
        entity_type="TestProfile",
        entity_id=profile.id,
        action="UPDATE",
        actor="Administrator",
        details_json=json.dumps(updates, default=str),
    ))
    db.commit()
    db.refresh(profile)
    return profile
