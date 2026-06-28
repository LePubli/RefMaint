from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.panne import Panne
from app.schemas.panne import PanneCreate, PanneUpdate, PanneOut
from app.core.security import get_current_user
from app.core.activity import log_activity

router = APIRouter(prefix="/api/pannes", tags=["pannes"])


@router.get("/", response_model=list[PanneOut])
def list_pannes(skip: int = 0, limit: int = 100, machine_id: int = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Panne)
    if machine_id:
        q = q.filter(Panne.machine_id == machine_id)
    return q.offset(skip).limit(limit).all()


@router.get("/{panne_id}", response_model=PanneOut)
def get_panne(panne_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    panne = db.query(Panne).filter(Panne.id == panne_id).first()
    if not panne:
        raise HTTPException(status_code=404, detail="Panne not found")
    return panne


@router.post("/", response_model=PanneOut)
def create_panne(panne_in: PanneCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    panne = Panne(**panne_in.model_dump())
    db.add(panne)
    db.commit()
    db.refresh(panne)
    log_activity(db, current_user, "créé", "panne", panne.id, panne.titre)
    return panne


@router.put("/{panne_id}", response_model=PanneOut)
def update_panne(panne_id: int, panne_in: PanneUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    panne = db.query(Panne).filter(Panne.id == panne_id).first()
    if not panne:
        raise HTTPException(status_code=404, detail="Panne not found")
    for key, value in panne_in.model_dump(exclude_unset=True).items():
        setattr(panne, key, value)
    db.commit()
    db.refresh(panne)
    log_activity(db, current_user, "modifié", "panne", panne.id, panne.titre)
    return panne


@router.delete("/{panne_id}")
def delete_panne(panne_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    panne = db.query(Panne).filter(Panne.id == panne_id).first()
    if not panne:
        raise HTTPException(status_code=404, detail="Panne not found")
    label = panne.titre
    db.delete(panne)
    db.commit()
    log_activity(db, current_user, "supprimé", "panne", panne_id, label)
    return {"ok": True}


@router.get("/export/csv")
def export_pannes_csv(db: Session = Depends(get_db), _=Depends(get_current_user)):
    from fastapi.responses import StreamingResponse
    import csv, io
    pannes = db.query(Panne).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "machine_id", "titre", "criticite", "cause_reelle", "solution", "temps_moyen_reparation", "created_at"])
    for p in pannes:
        writer.writerow([p.id, p.machine_id, p.titre, p.criticite, p.cause_reelle, p.solution, p.temps_moyen_reparation, p.created_at])
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.read().encode()), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=pannes.csv"})
