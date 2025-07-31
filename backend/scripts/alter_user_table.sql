-- Make email nullable and phone not nullable
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
-- Add unique constraint to phone
ALTER TABLE users ADD CONSTRAINT users_phone_key UNIQUE (phone);
-- Add index to phone for faster lookups
CREATE INDEX IF NOT EXISTS ix_users_phone ON users (phone);
