Create Database VodenjeHelikopterjev;
Use VodenjeHelikopterjev;
/*Create tables*/
Create Table Helikopterji(
	ID Integer Primary Key,
	Ime	Varchar(50) Not Null,
	Model Varchar(50),
	LetoIzdelave Integer,
	Cena Decimal(18,2),
	IsDeleted Bit Not Null Default 0,
	DateInserted Datetime Not Null,
	DateDeleted Datetime,
	Najet Bit Not Null Default 0
);
CREATE INDEX idxIme ON Helikopterji (Ime);
CREATE INDEX idxNajet ON Helikopterji (Najet);
Create Table Ljudje(
	ID Integer Primary Key,
	Ime Varchar(50) Not Null,
	Priimek Varchar(50) Not Null,
	Spol Varchar(1)  Not Null,
	Država Varchar(50)  Not Null,
	DatumRojstva Date  Not Null,
	EMŠO Varchar(18)  Not Null,
	Bivališèe Varchar(50),
	DateInserted Datetime Not Null
);
Create Table DovoljenjaZaPilotiranje(
	ID Integer Primary Key,
	IDCloveka Integer Not Null Foreign Key References Ljudje(ID),
	DatumPotekaVeljavnosti Date Not Null,
	DatumIzdaje Date Not Null,
	DateInserted Datetime Not Null
);
Create Table Izposoje(
	ID Integer Primary Key,
	DatumIzposoje Date Not Null,
	DatumVrnitve Date Not Null,
	IDModela Integer Not Null Foreign Key References Helikopterji(ID),
	IDCloveka Integer Not Null Foreign Key References Ljudje(ID),
	StatusIzposoje Bit Not Null Default 0
);
GO
/*Creating no delete Trigger on tables*/
CREATE TRIGGER NoDeleteLjudje ON Ljudje INSTEAD OF DELETE AS RAISERROR('You cant delete from this table', 16, 10);
GO
CREATE TRIGGER NoDeleteDovoljenjaZaPilotiranje ON DovoljenjaZaPilotiranje INSTEAD OF DELETE AS RAISERROR('You cant delete from this table', 16, 10);
GO
CREATE TRIGGER NoDeleteIzposoje ON Izposoje INSTEAD OF DELETE AS RAISERROR('You cant delete from this table', 16, 10);
GO
/*Create procedures*/
CREATE PROCEDURE AddHelicopter
AS
	Declare
	@Ime As	Varchar(50),
	@Model As Varchar(50),
	@LetoIzdelave As Integer,
	@Cena As Decimal(18,2)
	BEGIN
		INSERT INTO Helikopterji (Ime,Model,LetoIzdelave,Cena,DateInserted,IsDeleted,Najet) 
		VALUES (@Ime,@Model,@LetoIzdelave,@Cena,Getdate(),0,0)
	END
GO
CREATE PROCEDURE DeleteHelicopter
AS
	Declare
	@ID As Integer
	BEGIN
		UPDATE Helikopterji
		SET IsDeleted=1,DateDeleted=getdate()
		WHERE ID=@ID;
	END
GO
CREATE PROCEDURE GetListOfHelicopters
AS
	BEGIN
		Select Ime,Model,LetoIzdelave,Cena,Najet From Helikopterji
	END
GO