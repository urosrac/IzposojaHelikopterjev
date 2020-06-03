import os
from sqla_wrapper import SQLAlchemy
from sqlalchemy import ForeignKey
db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))
class Helicopter(db.Model):
    __tablename__ = 'helicopters'
    ID = db.Column(db.Integer, primary_key=True)
    Ime = db.Column(db.String, nullable=False)
    Model = db.Column(db.String, nullable=False)
    LetoIzdelave = db.Column(db.DateTime, nullable=False)
    Cena = db.Column(db.Float, nullable=False)
    IsDeleted = db.Column(db.Boolean, nullable=False, index=True)
    Rented = db.Column(db.Boolean, nullable=False, index=True)
class Persons(db.Model):
    __tablename__ = 'persons'
    ID = db.Column(db.Integer, primary_key=True)
    PersonName = db.Column(db.String, nullable=True)
    PersonLastName = db.Column(db.String, nullable=True)
    PersonEMSO = db.Column(db.String, nullable=True)
    PersonCountry = db.Column(db.String, nullable=True)
    PersonEmailAddress = db.Column(db.String, nullable=True)
    DateInserted = db.Column(db.DateTime, nullable=True)
    DateModified = db.Column(db.DateTime, nullable=True)
    PersonUserName = db.Column(db.String, nullable=False, index=True)
    PersonPassword = db.Column(db.String, nullable=False)
    PriorityType = db.Column(db.Integer, nullable=False, index=True)
    SessionToken = db.Column(db.String, nullable=True, index=True)
    IsDeleted = db.Column(db.Boolean, nullable=False, index=True)
class Izposoje(db.Model):
    __tablename__ = 'izposojes'
    ID = db.Column(db.Integer, primary_key=True)
    DatumIzposoje = db.Column(db.DateTime, nullable=False)
    DatumVrnitve = db.Column(db.DateTime, nullable=True)
    IDModela = db.Column(db.Integer, ForeignKey("helicopters.ID"), index=True)
    IDCloveka = db.Column(db.Integer, ForeignKey('persons.ID'), index=True)
    IsReturned = db.Column(db.Boolean, nullable=False, index=True)