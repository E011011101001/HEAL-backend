BEGIN;

-- CREATE TABLE "User" -----------------------------------------
CREATE TABLE "User"(
	"UserID" Integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	"Type" Integer NOT NULL,
	"Name" Text NOT NULL,
	"Age" Integer,
	"Address" Text,
	"Height" Real,
	"Weight" Real,
CONSTRAINT "unique_UserID" UNIQUE ( UserID ) );
-- -------------------------------------------------------------

COMMIT;

BEGIN;

-- CREATE TABLE "Session" --------------------------------------
CREATE TABLE "Session"(
	"SessionID" Text NOT NULL,
	"IsValid" Boolean NOT NULL DEFAULT 1,
	"UserID" Integer,
    "ValidUntil" DateTime NOT NULL DEFAULT (datetime('now', '+172800 seconds')),
	CONSTRAINT "lnk_User_Session" FOREIGN KEY ( "UserID" ) REFERENCES "User"( "UserID" )
		ON DELETE Cascade
		ON UPDATE Cascade
,
CONSTRAINT "unique_SessionID" UNIQUE ( SessionID ) );
-- -------------------------------------------------------------

-- CREATE INDEX "index_User_id" --------------------------------
CREATE INDEX "index_User_id" ON "Session"( "UserID" );
-- -------------------------------------------------------------

COMMIT;
