CREATE TABLE "${flyway:defaultSchema}".coordinates (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK (id > 0),
 version bigint NOT NULL DEFAULT 0,
 x bigint NOT NULL,
 y double precision NOT NULL CHECK (y > -531 AND y < 'Infinity'::float8)
);
CREATE TABLE "${flyway:defaultSchema}".human (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK (id > 0),
 version bigint NOT NULL DEFAULT 0,
 name text NOT NULL CHECK (length(btrim(name)) > 0),
 age integer NOT NULL CHECK (age > 0),
 height real NOT NULL CHECK (height > 0 AND height < 'Infinity'::real),
 birthday timestamptz CHECK (isfinite(birthday))
);
CREATE TABLE "${flyway:defaultSchema}".city (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK (id > 0),
 version bigint NOT NULL DEFAULT 0,
 name text NOT NULL CHECK (length(btrim(name)) > 0),
 coordinates_id bigint NOT NULL REFERENCES "${flyway:defaultSchema}".coordinates(id) ON DELETE RESTRICT,
 creation_date date NOT NULL DEFAULT (now() AT TIME ZONE 'UTC')::date CHECK (isfinite(creation_date)),
 area real NOT NULL CHECK (area > 0 AND area < 'Infinity'::real),
 population bigint NOT NULL CHECK (population > 0),
 establishment_date timestamp CHECK (isfinite(establishment_date)),
 capital boolean NOT NULL,
 meters_above_sea_level bigint,
 climate varchar(40) CHECK (climate IN ('RAIN_FOREST','MONSOON','TROPICAL_SAVANNA','MEDITERRANIAN')),
 government varchar(40) CHECK (government IN ('ANARCHY','DESPOTISM','ETHNOCRACY')),
 standard_of_living varchar(40) NOT NULL CHECK (standard_of_living IN ('ULTRA_HIGH','VERY_HIGH','LOW','VERY_LOW','NIGHTMARE')),
 governor_id bigint REFERENCES "${flyway:defaultSchema}".human(id) ON DELETE RESTRICT
);
CREATE INDEX city_coordinates_idx ON "${flyway:defaultSchema}".city(coordinates_id);
CREATE INDEX city_governor_idx ON "${flyway:defaultSchema}".city(governor_id);
CREATE INDEX city_name_idx ON "${flyway:defaultSchema}".city(name);
CREATE FUNCTION "${flyway:defaultSchema}".protect_city_generated_fields() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP = 'INSERT' THEN NEW.creation_date := (now() AT TIME ZONE 'UTC')::date;
 ELSE
  IF NEW.id <> OLD.id OR NEW.creation_date <> OLD.creation_date THEN
   RAISE EXCEPTION 'id and creationDate are immutable' USING ERRCODE = '23514';
  END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER city_generated BEFORE INSERT OR UPDATE ON "${flyway:defaultSchema}".city
 FOR EACH ROW EXECUTE FUNCTION "${flyway:defaultSchema}".protect_city_generated_fields();

-- A committed, monotonic revision shared by all app instances and browsers.
CREATE TABLE "${flyway:defaultSchema}".revision (id integer PRIMARY KEY CHECK (id = 1), value bigint NOT NULL);
INSERT INTO "${flyway:defaultSchema}".revision VALUES (1, 0);
CREATE FUNCTION "${flyway:defaultSchema}".bump_revision() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 UPDATE "${flyway:defaultSchema}".revision SET value = value + 1 WHERE id = 1;
 RETURN NULL;
END $$;
CREATE TRIGGER city_revision AFTER INSERT OR UPDATE OR DELETE ON "${flyway:defaultSchema}".city
 FOR EACH STATEMENT EXECUTE FUNCTION "${flyway:defaultSchema}".bump_revision();
CREATE TRIGGER coordinates_revision AFTER INSERT OR UPDATE OR DELETE ON "${flyway:defaultSchema}".coordinates
 FOR EACH STATEMENT EXECUTE FUNCTION "${flyway:defaultSchema}".bump_revision();
CREATE TRIGGER human_revision AFTER INSERT OR UPDATE OR DELETE ON "${flyway:defaultSchema}".human
 FOR EACH STATEMENT EXECUTE FUNCTION "${flyway:defaultSchema}".bump_revision();

