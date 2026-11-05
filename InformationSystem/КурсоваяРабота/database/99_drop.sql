\set ON_ERROR_STOP on
\encoding UTF8
-- Запускать только для удаления учебной схемы fleet вместе с её данными.
BEGIN;
DROP SCHEMA fleet CASCADE;
COMMIT;
