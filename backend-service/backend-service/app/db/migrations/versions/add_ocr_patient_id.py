"""Add ocr_patient_id

Revision ID: add_ocr_patient_id
Revises: 96e2434a5f94
Create Date: 2026-04-03 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_ocr_patient_id'
down_revision: Union[str, None] = '96e2434a5f94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('patients', sa.Column('ocr_patient_id', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_patients_ocr_patient_id'), 'patients', ['ocr_patient_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_patients_ocr_patient_id'), table_name='patients')
    op.drop_column('patients', 'ocr_patient_id')
