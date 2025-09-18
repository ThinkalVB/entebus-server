from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from app.src import buckets, minio
from app.src.db import get_db_url, engine


def _alembic_cfg() -> Config:
    alembic_cfg = Config("app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", get_db_url())
    return alembic_cfg


def migrate():
    """Run migrations up to head. Only applies existing revisions."""
    alembic_cfg = _alembic_cfg()
    command.upgrade(alembic_cfg, "head")
    print("* Database migrated to head")


def upgrade(message="auto upgrade"):
    """
    Compare current DB with models, create a revision if needed, and apply it.
    Works for first-time migrations as well.
    """
    alembic_cfg = _alembic_cfg()
    script = ScriptDirectory.from_config(alembic_cfg)

    # If no revisions exist, create initial revision
    if not list(script.walk_revisions(base="base", head="heads")):
        print("* No revisions found, creating initial revision")
        command.revision(alembic_cfg, message="initial schema", autogenerate=True)
        command.upgrade(alembic_cfg, "head")
        return

    # Make sure DB is at head
    command.upgrade(alembic_cfg, "head")

    # Now generate a new revision based on model differences
    print("* Generating new revision for model changes...")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    command.upgrade(alembic_cfg, "head")
    print("* Database upgraded to head")


def reset_db():
    """Drop everything and recreate schema from migrations."""
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
    print("* Database schema reset")

    migrate()


def downgrade(step="-1"):
    command.downgrade(_alembic_cfg(), step)
    print(f"* Database downgraded to {step}")


def create_buckets():
    for bucket in buckets.ALL:
        minio.create_bucket(bucket)
    print("* Buckets created")


def delete_buckets():
    for bucket in buckets.ALL:
        minio.delete_bucket(bucket)
    print("* Buckets deleted")


if __name__ == "__main__":
    import sys

    actions = {
        "migrate": migrate,
        "upgrade": upgrade,
        "reset_db": reset_db,
        "downgrade": downgrade,
        "create_buckets": create_buckets,
        "delete_buckets": delete_buckets,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        print(
            "Usage: python setup.py [migrate|upgrade|reset_db|downgrade|create_buckets|delete_buckets]"
        )
        sys.exit(1)

    action = sys.argv[1]

    if action == "downgrade":
        step = sys.argv[2] if len(sys.argv) > 2 else "-1"
        actions[action](step)
    elif action == "upgrade":
        message = sys.argv[2] if len(sys.argv) > 2 else "auto upgrade"
        actions[action](message)
    else:
        actions[action]()
