# Imports pour Alembic autogenerate et accès centralisé.
from app.models.user import User
from app.models.machine import Machine
from app.models.panne import Panne
from app.models.intervention import Intervention
from app.models.piece import Piece, PannesPieces
from app.models.activity_log import ActivityLog
from app.models.notification import Notification, NotificationRead
from app.models.maintenance_preventive import MaintenancePreventive

__all__ = [
    "User",
    "Machine",
    "Panne",
    "Intervention",
    "Piece",
    "PannesPieces",
    "ActivityLog",
    "Notification",
    "NotificationRead",
    "MaintenancePreventive",
]
