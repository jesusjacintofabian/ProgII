from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security.auth import get_current_user, registrar_auditoria
from app.security.permissions import requiere_rol

router = APIRouter(prefix="/mesa-ayuda", tags=["Mesa de Ayuda - Grupo 2"])


@router.post("/tickets", response_model=schemas.TicketOut)
def crear_ticket(datos: schemas.TicketCreate, request: Request,
                  db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    ticket = models.Ticket(usuario_id=usuario.id, **datos.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    registrar_auditoria(db, "CREATE_TICKET", f"Ticket {ticket.id} creado",
                         usuario_id=usuario.id, ip=request.client.host)
    return ticket


@router.get("/tickets", response_model=list[schemas.TicketOut])
def listar_tickets(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    """Un usuario normal solo ve sus propios tickets. Soporte/Admin ven todos."""
    query = db.query(models.Ticket)
    if usuario.rol.nombre == "Usuario":
        query = query.filter(models.Ticket.usuario_id == usuario.id)
    return query.order_by(models.Ticket.creado_en.desc()).all()


@router.get("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def obtener_ticket(ticket_id: int, db: Session = Depends(get_db),
                    usuario=Depends(get_current_user)):
    ticket = db.get(models.Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if usuario.rol.nombre == "Usuario" and ticket.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este ticket")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=schemas.TicketOut,
              dependencies=[Depends(requiere_rol("Administrador", "Soporte"))])
def actualizar_ticket(ticket_id: int, datos: schemas.TicketUpdate, request: Request,
                       db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    ticket = db.get(models.Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(ticket, campo, valor)

    db.commit()
    db.refresh(ticket)

    registrar_auditoria(db, "UPDATE_TICKET", f"Ticket {ticket.id} actualizado",
                         usuario_id=usuario.id, ip=request.client.host)
    return ticket
