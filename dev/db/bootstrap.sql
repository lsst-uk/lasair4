-- One-time setup of the local MariaDB for the Lasair dev stack.
-- Run as a MariaDB admin user:  mysql -u root -p < dev/db/bootstrap.sql
-- The dev stack uses its own database, `lasair_dev`, so it never touches an
-- existing `ztf` database. CREATE DATABASE fails on purpose if `lasair_dev`
-- already exists, so an existing database is never reused by accident.

-- utf8mb4 MAKES THE myqueries ROW TOO LARGE FOR MARIADB. utf8mb3_unicode_ci MATCHES THE objectId
-- COLLATION IN common/schema, SO JOINS BETWEEN TABLES DO NOT MIX COLLATIONS.
CREATE DATABASE lasair_dev CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci;

CREATE USER IF NOT EXISTS 'lasair_dev_rw'@'localhost' IDENTIFIED BY 'lasair_dev_rw';
CREATE USER IF NOT EXISTS 'lasair_dev_rw'@'127.0.0.1' IDENTIFIED BY 'lasair_dev_rw';
CREATE USER IF NOT EXISTS 'lasair_dev_ro'@'localhost' IDENTIFIED BY 'lasair_dev_ro';
CREATE USER IF NOT EXISTS 'lasair_dev_ro'@'127.0.0.1' IDENTIFIED BY 'lasair_dev_ro';

GRANT ALL PRIVILEGES ON lasair_dev.* TO 'lasair_dev_rw'@'localhost', 'lasair_dev_rw'@'127.0.0.1';
GRANT SELECT, CREATE TEMPORARY TABLES, EXECUTE ON lasair_dev.* TO 'lasair_dev_ro'@'localhost', 'lasair_dev_ro'@'127.0.0.1';

-- jdnow() IS USED BY FILTERS AND THE FRONT PAGE. PRODUCTION DEFINES IT OUTSIDE THIS REPO.
USE lasair_dev;
CREATE FUNCTION jdnow() RETURNS DOUBLE NOT DETERMINISTIC NO SQL
    RETURN UNIX_TIMESTAMP(NOW(6)) / 86400.0 + 2440587.5;

FLUSH PRIVILEGES;
