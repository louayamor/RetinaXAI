"""Add modality to mri_scans

Revision ID: add_mri_scans_modality
Revises: add_oct_reports
Create Date: 2026-04-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_mri_scans_modality'
down_revision: Union[str, None] = 'add_oct_reports'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'mri_scans',
        sa.Column('modality', sa.String(length=50), nullable=False, server_default='fundus')
    )


def downgrade() -> None:
    op.drop_column('mri_scans', 'modality')
