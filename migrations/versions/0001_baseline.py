"""Initial MediLink schema from ER diagram with documented API-alignment changes.

Apply only to an empty database. Existing databases must be reconciled before stamping.
The immutable SQL snapshot keeps later ORM edits out of this revision.
"""

from pathlib import Path

from alembic import op

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    sql = (Path(__file__).parent / "0001_baseline.sql").read_text()
    for statement in sql.split(";"):
        if statement.strip():
            op.execute(statement)


def downgrade():
    raise RuntimeError(
        "Destructive baseline downgrade is intentionally disabled; restore a verified backup."
    )
