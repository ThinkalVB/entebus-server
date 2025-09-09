from sqlalchemy import text
from app.src.db import ORMbase, engine


def remove_tables():
    """Drop all tables defined in ORMbase metadata."""
    ORMbase.metadata.drop_all(engine)
    print("* All tables deleted")


def create_tables():
    """Create all tables defined in ORMbase metadata and add triggers."""
    ORMbase.metadata.create_all(engine)
    print("* All tables created")

    with engine.begin() as conn:
        # --- Wallet Trigger ---
        conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION prevent_wallet_delete()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Allow deletion only if balance = 0
                IF OLD.balance <> 0 THEN
                    RAISE EXCEPTION 'Cannot delete wallet unless balance is zero'
                    USING ERRCODE = '45000';
                END IF;
                RETURN OLD;
            END;
            $$ LANGUAGE plpgsql;
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE OR REPLACE TRIGGER wallet_delete_trigger
            BEFORE DELETE ON wallet
            FOR EACH ROW
            EXECUTE FUNCTION prevent_wallet_delete();
        """
            )
        )

    print("* Triggers created")


if __name__ == "__main__":
    create_tables()
    remove_tables()
