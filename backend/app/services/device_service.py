import json

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models.device import Device
from app.database.models.audit import AuditEvent
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceConflictError(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass


def create_device(db: Session, payload: DeviceCreate) -> Device:
    existing = db.scalar(select(Device).where(Device.part_number == payload.part_number))
    if existing:
        raise DeviceConflictError("A device with this part number already exists")

    device = Device(**payload.model_dump())
    db.add(device)
    db.flush()
    db.add(AuditEvent(
        entity_type="Device",
        entity_id=device.id,
        action="CREATE",
        actor="Administrator",
        details_json=json.dumps({"part_number": device.part_number}),
    ))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DeviceConflictError("A device with this part number already exists") from exc
    db.refresh(device)
    return device


def list_devices(
    db: Session,
    search: str | None = None,
    device_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Device]:
    statement = select(Device).order_by(Device.created_at.desc())
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(Device.part_number.ilike(pattern), Device.manufacturer.ilike(pattern))
        )
    if device_type:
        statement = statement.where(Device.device_type == device_type)
    statement = statement.limit(limit).offset(offset)
    return list(db.scalars(statement).all())


def get_device(db: Session, device_id: str) -> Device:
    device = db.get(Device, device_id)
    if not device:
        raise DeviceNotFoundError("Device not found")
    return device


def update_device(db: Session, device_id: str, payload: DeviceUpdate) -> Device:
    device = get_device(db, device_id)
    updates = payload.model_dump(exclude_unset=True)

    if "part_number" in updates:
        existing = db.scalar(
            select(Device).where(
                Device.part_number == updates["part_number"],
                Device.id != device_id,
            )
        )
        if existing:
            raise DeviceConflictError("A device with this part number already exists")

    for field, value in updates.items():
        setattr(device, field, value)

    try:
        db.add(AuditEvent(
            entity_type="Device",
            entity_id=device.id,
            action="UPDATE",
            actor="Administrator",
            details_json=json.dumps(updates, default=str),
        ))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DeviceConflictError("A device with this part number already exists") from exc
    db.refresh(device)
    return device
