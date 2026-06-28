from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.intervention import Intervention
from app.schemas.intervention import InterventionCreate, InterventionUpdate, InterventionOut
from app.core.security import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/api/interventions", tags=["interventions"])


@router.get("/", response_model=list[InterventionOut])
def list_interventions(skip: int = 0, limit: int = 100, machine_id: int = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Intervention)
    if machine_id:
        q = q.filter(Intervention.machine_id == machine_id)
    return q.order_by(Intervention.date_intervention.desc()).offset(skip).limit(limit).all()


@router.get("/{intervention_id}", response_model=InterventionOut)
def get_intervention(intervention_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inter = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not inter:
        raise HTTPException(status_code=404, detail="Intervention not found")
    return inter


@router.post("/", response_model=InterventionOut)
def create_intervention(inter_in: InterventionCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inter = Intervention(**inter_in.model_dump())
    db.add(inter)
    db.commit()
    db.refresh(inter)
    return inter


@router.put("/{intervention_id}", response_model=InterventionOut)
def update_intervention(intervention_id: int, inter_in: InterventionUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inter = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not inter:
        raise HTTPException(status_code=404, detail="Intervention not found")
    for key, value in inter_in.model_dump(exclude_unset=True).items():
        setattr(inter, key, value)
    db.commit()
    db.refresh(inter)
    return inter


@router.post("/{intervention_id}/valider", response_model=InterventionOut)
def valider_intervention(intervention_id: int, db: Session = Depends(get_db), current_user=Depends(require_manager_or_admin)):
    inter = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not inter:
        raise HTTPException(status_code=404, detail="Intervention not found")
    inter.validee = True
    inter.validee_par = current_user.username
    db.commit()
    db.refresh(inter)
    return inter


@router.delete("/{intervention_id}")
def delete_intervention(intervention_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inter = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not inter:
        raise HTTPException(status_code=404, detail="Intervention not found")
    db.delete(inter)
    db.commit()
    return {"ok": True}
