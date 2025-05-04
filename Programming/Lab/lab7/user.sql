BEGIN;

DROP TYPE IF EXISTS unit_of_measure_type CASCADE;
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

CREATE type unit_of_measure_type AS ENUM (
    'CENTIMETERS',
    'SQUARE_METERS',
    'LITERS',
    'MILLILITERS'
    );

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    permissions TEXT[] DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    org_name VARCHAR(255) NOT NULL,
    full_name VARCHAR(1125) UNIQUE NOT NULL,
    org_type organization_type NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price BIGINT NOT NULL,
    unit_of_measure unit_of_measure_type,
    manufacturer_id INT REFERENCES organizations(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS coordinates (
    product_id BIGINT PRIMARY KEY REFERENCES products(id),
    x DOUBLE PRECISION NOT NULL CHECK (x > -401),
    y REAL NOT NULL CHECK (y <= 569)
);


-- pro__id 自增
ALTER TABLE products
    ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;

END;
