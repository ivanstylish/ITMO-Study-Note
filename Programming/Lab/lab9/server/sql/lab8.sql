BEGIN;

DROP TYPE IF EXISTS unit_of_measure CASCADE;
DROP TYPE IF EXISTS organization_type CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS coordinates CASCADE;

CREATE type organization_type AS ENUM (
  'COMMERCIAL',
  'PUBLIC',
  'TRUST',
  'PRIVATE_LIMITED_COMPANY',
  'OPEN_JOINT_STOCK_COMPANY'
  );

CREATE type unit_of_measure AS ENUM (
  'CENTIMETERS',
  'SQUARE_METERS',
  'LITERS',
  'MILLILITERS'
  );

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(40) UNIQUE NOT NULL,
  password_digest VARCHAR(64) NOT NULL,
  salt VARCHAR(10) NOT NULL
  );

CREATE TABLE IF NOT EXISTS organizations (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL CONSTRAINT not_empty_name CHECK(length(name) > 0),
  employees_count BIGINT NOT NULL CONSTRAINT positive_employees_count CHECK (employees_count > 0),
  type organization_type NOT NULL,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE
  );

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL CONSTRAINT not_empty_name CHECK(length(name) > 0),
  x INTEGER NOT NULL,
  y BIGINT NOT NULL,
  creation_date DATE DEFAULT NOW() NOT NULL,
  price BIGINT NOT NULL CONSTRAINT positive_price CHECK (price > 0),
  unit_of_measure unit_of_measure,
  manufacturer_id INT REFERENCES organizations(id) ON DELETE SET NULL,
  creator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE
  );

END;
