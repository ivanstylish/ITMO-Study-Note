CREATE TABLE "${flyway:defaultSchema}".app_user (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK (id > 0),
 username varchar(32) NOT NULL UNIQUE CHECK (username ~ '^[a-z0-9_]{3,32}$'),
 password_hash varchar(60) NOT NULL CHECK (length(password_hash) = 60),
 registered_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'UTC')
);
-- No default accounts: register through the application.

