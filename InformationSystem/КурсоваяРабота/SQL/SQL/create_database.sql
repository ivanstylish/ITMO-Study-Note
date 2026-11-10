\set ON_ERROR_STOP on
\if :{?dbname}
CREATE DATABASE :"dbname" ENCODING 'UTF8' TEMPLATE template0;
\else
\echo 'Supply -v dbname=your_coursework_database'
DO $$BEGIN RAISE EXCEPTION 'Database parameters rejected';END$$;
\endif
