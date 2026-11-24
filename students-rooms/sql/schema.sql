-- ROOMS - a table for containing room id and room name.
CREATE TABLE IF NOT EXISTS rooms (
	id 			INT PRIMARY KEY,
	name		VARCHAR(50) NOT NULL
);

-- A trigger to automatically make a room name in case one is missing.
-- Doesn't replace imported existing room names.
CREATE OR REPLACE FUNCTION set_default_room_name()
RETURNS TRIGGER AS $$
BEGIN
	IF NEW.name IS NULL OR NEW.name = '' THEN
		NEW.name := 'Room #' || NEW.id::text;
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_rooms_default_name ON rooms;
CREATE TRIGGER trg_rooms_default_name
BEFORE INSERT ON rooms
FOR EACH ROW
EXECUTE FUNCTION set_default_room_name();

CREATE TABLE IF NOT EXISTS students (
	id			INT PRIMARY KEY,
	birthday	TIMESTAMP NOT NULL,
	name		VARCHAR(100) NOT NULL,
	room		INT REFERENCES rooms(id),
	sex			CHAR(1) NOT NULL
);