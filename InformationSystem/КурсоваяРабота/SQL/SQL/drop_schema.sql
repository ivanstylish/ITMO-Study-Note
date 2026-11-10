\set ON_ERROR_STOP on
\if :{?schema}
\else
DO $$BEGIN RAISE EXCEPTION 'Supply schema';END$$;
\endif
\if :{?confirm_schema}
\else
DO $$BEGIN RAISE EXCEPTION 'Supply confirm_schema';END$$;
\endif
SELECT :'schema'=:'confirm_schema' AND :'schema' NOT IN ('public','information_schema')
 AND :'schema' !~ '^pg_' AND EXISTS(
 SELECT 1 FROM pg_namespace WHERE nspname=:'schema'
 AND nspowner=(SELECT oid FROM pg_roles WHERE rolname=current_user)) AS permitted \gset
\if :permitted
DROP SCHEMA :"schema" CASCADE;
\else
DO $$BEGIN RAISE EXCEPTION 'Schema confirmation or ownership check failed';END$$;
\endif
