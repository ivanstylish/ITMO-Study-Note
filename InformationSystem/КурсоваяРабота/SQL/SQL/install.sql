\set ON_ERROR_STOP on
\if :{?schema}
\else
\set schema public
\endif
BEGIN;
SET LOCAL search_path TO :"schema", pg_catalog;
\ir 01_schema.sql
\ir 02_triggers.sql
\ir 03_comments.sql
\ir 04_operations.sql
\ir 05_indexes.sql
\ir 06_notifications.sql
COMMIT;
