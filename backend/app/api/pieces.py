from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.piece import Piece
from app.schemas.piece import PieceCreate, PieceUpdate, PieceOut
from app.core.security import get_current_user

router = APIRouter(prefix="/api/pieces", tags=["pieces"])


@router.get("/", response_model=list[PieceOut])
def list_pieces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Piece).offset(skip).limit(limit).all()


@router.get("/{piece_id}", response_model=PieceOut)
def get_piece(piece_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    return piece


@router.post("/", response_model=PieceOut)
def create_piece(piece_in: PieceCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    existing = db.query(Piece).filter(Piece.reference == piece_in.reference).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reference already exists")
    piece = Piece(**piece_in.model_dump())
    db.add(piece)
    db.commit()
    db.refresh(piece)
    return piece


@router.put("/{piece_id}", response_model=PieceOut)
def update_piece(piece_id: int, piece_in: PieceUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    for key, value in piece_in.model_dump(exclude_unset=True).items():
        setattr(piece, key, value)
    db.commit()
    db.refresh(piece)
    return piece


@router.delete("/{piece_id}")
def delete_piece(piece_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    db.delete(piece)
    db.commit()
    return {"ok": True}
