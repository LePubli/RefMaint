"""indexes on foreign keys + check constraints

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-13 00:00:00.000000

Index FK columns (machine_id, panne_id, piece_id) for query performance and
CHECK constraints to enforce valid enum-like values at the DB level.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Index sur les clés étrangères ( performances des jointures/filtres ) ---
    op.create_index("ix_pannes_machine_id", "pannes", ["machine_id"])
    op.create_index("ix_interventions_machine_id", "interventions", ["machine_id"])
    op.create_index("ix_interventions_panne_id", "interventions", ["panne_id"])
    op.create_index("ix_pannes_pieces_panne_id", "pannes_pieces", ["panne_id"])
    op.create_index("ix_pannes_pieces_piece_id", "pannes_pieces", ["piece_id"])
    op.create_index(
        "ix_maintenances_preventives_machine_id",
        "maintenances_preventives", ["machine_id"],
    )

    # --- Contraintes CHECK ( cohérence des enums au niveau base ) ---
    op.create_check_constraint(
        "ck_machines_statut",
        "machines",
        sa.text("statut IN ('operationnel', 'en_panne', 'maintenance', 'arrete')"),
    )
    op.create_check_constraint(
        "ck_pannes_criticite",
        "pannes",
        sa.text("criticite IS NULL OR (criticite >= 1 AND criticite <= 5)"),
    )
    op.create_check_constraint(
        "ck_users_role",
        "users",
        sa.text("role IN ('admin', 'manager', 'technicien')"),
    )
    op.create_check_constraint(
        "ck_pieces_stock",
        "pieces",
        sa.text("stock IS NULL OR stock >= 0"),
    )


def downgrade() -> None:
    op.drop_constraint("ck_pieces_stock", "pieces", type_="check")
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_constraint("ck_pannes_criticite", "pannes", type_="check")
    op.drop_constraint("ck_machines_statut", "machines", type_="check")
    op.drop_index("ix_maintenances_preventives_machine_id", table_name="maintenances_preventives")
    op.drop_index("ix_pannes_pieces_piece_id", table_name="pannes_pieces")
    op.drop_index("ix_pannes_pieces_panne_id", table_name="pannes_pieces")
    op.drop_index("ix_interventions_panne_id", table_name="interventions")
    op.drop_index("ix_interventions_machine_id", table_name="interventions")
    op.drop_index("ix_pannes_machine_id", table_name="pannes")
