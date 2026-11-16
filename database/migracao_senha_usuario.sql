-- Execute no banco projetoi antes de utilizar o login.
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS senha_hash TEXT;
