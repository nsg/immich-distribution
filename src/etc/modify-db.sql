-- An audit log of deleted assets
CREATE TABLE IF NOT EXISTS assets_delete_audits (
    id INT GENERATED ALWAYS AS IDENTITY,
    asset_id UUID NOT NULL,
    user_id VARCHAR(256) NULL,
    checksum BYTEA,
    file_removed BOOLEAN DEFAULT FALSE,
    changed_on TIMESTAMP(6) NOT NULL
);

-- A lookup table for assets that are imported from the file system via sync feature
CREATE TABLE IF NOT EXISTS assets_filesync_lookup (
    id INT GENERATED ALWAYS AS IDENTITY,
    user_id VARCHAR(256) NULL,
    asset_path TEXT NOT NULL,
    checksum BYTEA,
    UNIQUE(user_id, asset_path)
);

-- Function that logs the deletion of assets
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

-- Trigger that calls the function above on deletion of assets
CREATE OR REPLACE TRIGGER trigger_assets_delete_audits
BEFORE DELETE ON asset
FOR EACH ROW
EXECUTE PROCEDURE log_assets_delete_audits();
