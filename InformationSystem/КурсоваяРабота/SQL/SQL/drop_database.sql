\set ON_ERROR_STOP on
\if :{?dbname}
\else
\echo 'Supply -v dbname=... and -v confirm_dbname=...'
DO $$BEGIN RAISE EXCEPTION 'Database parameters rejected';END$$;
\endif
\if :{?confirm_dbname}
\else
DO $$BEGIN RAISE EXCEPTION 'Database parameters rejected';END$$;
\endif
SELECT :'dbname'=:'confirm_dbname'
 AND :'dbname' ~ '^fleet_street_coursework(_[a-z0-9_]+)?$'
 AND current_database()='postgres' AS permitted \gset
\if :permitted
DROP DATABASE :"dbname";
\else
\echo 'Refused: connect to postgres and confirm the coursework database name.'
DO $$BEGIN RAISE EXCEPTION 'Database parameters rejected';END$$;
\endif
