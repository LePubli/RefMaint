import qrcode
import io
import base64
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineUpdate, MachineOut
from app.core.security import get_current_user

router = APIRouter(prefix="/api/machines", tags=["machines"])


def generate_qr(data: str) -> str:
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@router.get("/", response_model=list[MachineOut])
def list_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Machine).offset(skip).limit(limit).all()


@router.get("/{machine_id}", response_model=MachineOut)
def get_machine(machine_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


@router.post("/", response_model=MachineOut)
def create_machine(machine_in: MachineCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    machine = Machine(**machine_in.model_dump())
    db.add(machine)
    db.flush()
    machine.qr_code = generate_qr(f"trimaint://machine/{machine.id}")
    db.commit()
    db.refresh(machine)
    return machine


@router.put("/{machine_id}", response_model=MachineOut)
def update_machine(machine_id: int, machine_in: MachineUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    for key, value in machine_in.model_dump(exclude_unset=True).items():
        setattr(machine, key, value)
    db.commit()
    db.refresh(machine)
    return machine


@router.delete("/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(machine)
    db.commit()
    return {"ok": True}
