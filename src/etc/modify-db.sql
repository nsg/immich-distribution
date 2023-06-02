CREATE TABLE IF NOT EXISTS assets_delete_audits (
    id INT GENERATED ALWAYS AS IDENTITY,
    asset_id UUID NOT NULL,
    user_id VARCHAR(256) NULL,
    checksum BYTEA,
    file_removed BOOLEAN DEFAULT FALSE,
    changed_on TIMESTAMP(6) NOT NULL
);

CREATE TABLE IF NOT EXISTS assets_filesync_lookup (
    id INT GENERATED ALWAYS AS IDENTITY,
    user_id VARCHAR(256) NULL,
    asset_path TEXT NOT NULL UNIQUE,
    checksum BYTEA,
    UNIQUE(asset_path, checksum)
);

CREATE OR REPLACE FUNCTION log_assets_delete_audits()
    RETURNS TRIGGER
    LANGUAGE PLPGSQL
    AS
$$
BEGIN
    INSERT INTO assets_delete_audits(asset_id, user_id, checksum, changed_on)
    VALUES(OLD.id, OLD."ownerId", OLD.checksum, NOW());
    RETURN OLD;
END;
$$;

CREATE OR REPLACE TRIGGER trigger_assets_delete_audits
BEFORE DELETE ON assets
FOR EACH ROW
EXECUTE PROCEDURE log_assets_delete_audits();
