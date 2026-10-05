-- All five operations execute in PostgreSQL, not Java or JavaScript.
CREATE OR REPLACE FUNCTION "${flyway:defaultSchema}".average_elevation() RETURNS numeric LANGUAGE sql STABLE AS $$
 SELECT avg(meters_above_sea_level) FROM "${flyway:defaultSchema}".city
$$;
CREATE OR REPLACE FUNCTION "${flyway:defaultSchema}".group_by_area() RETURNS TABLE(area real, count bigint) LANGUAGE sql STABLE AS $$
 SELECT c.area, count(*) FROM "${flyway:defaultSchema}".city c GROUP BY c.area ORDER BY c.area
$$;
-- strpos means a literal, case-sensitive substring: % and _ are not wildcards.
CREATE OR REPLACE FUNCTION "${flyway:defaultSchema}".names_containing(needle text) RETURNS SETOF "${flyway:defaultSchema}".city LANGUAGE sql STABLE AS $$
 SELECT c.* FROM "${flyway:defaultSchema}".city c WHERE strpos(c.name, needle) > 0 ORDER BY c.id
$$;
CREATE OR REPLACE FUNCTION "${flyway:defaultSchema}".route_extreme_areas() RETURNS double precision LANGUAGE plpgsql STABLE AS $$
DECLARE largest "${flyway:defaultSchema}".city; smallest "${flyway:defaultSchema}".city; a "${flyway:defaultSchema}".coordinates; b "${flyway:defaultSchema}".coordinates;
BEGIN
 SELECT * INTO largest FROM "${flyway:defaultSchema}".city ORDER BY area DESC, id ASC LIMIT 1;
 IF NOT FOUND THEN RETURN NULL; END IF;
 SELECT * INTO smallest FROM "${flyway:defaultSchema}".city ORDER BY area ASC, id ASC LIMIT 1;
 IF largest.id = smallest.id THEN RETURN 0; END IF;
 IF largest.meters_above_sea_level IS NULL OR smallest.meters_above_sea_level IS NULL THEN
  RAISE EXCEPTION 'Cannot calculate route: an endpoint has no metersAboveSeaLevel' USING ERRCODE = '22023';
 END IF;
 SELECT * INTO a FROM "${flyway:defaultSchema}".coordinates WHERE id = largest.coordinates_id;
 SELECT * INTO b FROM "${flyway:defaultSchema}".coordinates WHERE id = smallest.coordinates_id;
 RETURN sqrt(power(a.x::float8 - b.x::float8, 2) + power(a.y - b.y, 2)
   + power(largest.meters_above_sea_level::float8 - smallest.meters_above_sea_level::float8, 2));
END $$;
CREATE OR REPLACE FUNCTION "${flyway:defaultSchema}".route_newest_city() RETURNS double precision LANGUAGE plpgsql STABLE AS $$
DECLARE newest "${flyway:defaultSchema}".city; point "${flyway:defaultSchema}".coordinates;
BEGIN
 SELECT * INTO newest FROM "${flyway:defaultSchema}".city WHERE establishment_date IS NOT NULL
 ORDER BY establishment_date DESC, id ASC LIMIT 1;
 IF NOT FOUND THEN RETURN NULL; END IF;
 IF newest.meters_above_sea_level IS NULL THEN
  RAISE EXCEPTION 'Cannot calculate route: newest city has no metersAboveSeaLevel' USING ERRCODE = '22023';
 END IF;
 SELECT * INTO point FROM "${flyway:defaultSchema}".coordinates WHERE id = newest.coordinates_id;
 RETURN sqrt(power(point.x::float8, 2) + power(point.y, 2) + power(newest.meters_above_sea_level::float8, 2));
END $$;


CREATE OR REPLACE FUNCTION "${flyway:defaultSchema}".bump_revision()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    UPDATE "${flyway:defaultSchema}".revision SET value = value + 1 WHERE id = 1;
    RETURN NULL;
END $$;