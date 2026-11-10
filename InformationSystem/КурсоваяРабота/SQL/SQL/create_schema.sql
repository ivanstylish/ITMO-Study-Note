\set ON_ERROR_STOP on
\if :{?schema}
CREATE SCHEMA :"schema";
\else
DO $$BEGIN RAISE EXCEPTION 'Supply -v schema=student_schema';END$$;
\endif
