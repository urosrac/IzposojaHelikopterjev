from flask import Flask, render_template, request, redirect, url_for, session, make_response
from models import Helicopter, Persons, Izposoje, db
import hashlib
from uuid import uuid4
from datetime import datetime
app = Flask(__name__)
db.create_all()
@app.route("/Logout")
def Logout():
    return redirect(url_for("LoginForm"))
@app.route("/index")
def index():
    return render_template("Admin/index.html")
@app.route("/")
def BeginRoute():
    return redirect(url_for("LoginForm"))
@app.route("/Login")
def LoginForm():
    if not db.query(Persons).filter_by(PersonUserName="admin").first():
        admin = Persons(PersonUserName = "admin",
                       PersonPassword = str(hashlib.sha256("admin".encode()).hexdigest()),
                       PriorityType = 1,
                       IsDeleted = 0)
        db.add(admin)
        db.commit()
    return render_template("Login/Login.html")
@app.route("/LogedUser", methods = ["GET", "POST"])
def LogedUser():
    UserName = request.form.get("UserName")
    HashedPassword = hashlib.sha256(request.form.get("Password").encode()).hexdigest()
    User = db.query(Persons).filter_by(PersonUserName = UserName, IsDeleted = 0).first()
    if User and User.PersonPassword == HashedPassword:
        session_token = str(uuid4())
        User.SessionToken = session_token
        db.add(User)
        db.commit()
        if User.PersonUserName == "admin":
            response = make_response(render_template("Admin/index.html"))
        else:
            response = make_response(render_template("User/index.html"))
        response.set_cookie("session_token", session_token, httponly = True, samesite = 'Strict')
        return response
    else:
        return render_template("Login/LoginFailed.html", message = "Prijava ni bila uspešna napačno uporabniško ime ali geslo.", Link="/Login")
@app.route("/Register")
def Register():
    return render_template("Login/Register.html")
@app.route("/RegisteredUser", methods = ["GET", "POST"])
def RegisteredUser():
    if request.method == "POST":
        session["PersonName"] = request.form.get("PersonName")
        session["PersonLastName"] = request.form.get("PersonLastName")
        session["PersonEMSO"] = request.form.get("PersonEMSO")
        session["PersonCountry"] = request.form.get("PersonCountry")
        session["PersonEmailAddress"] = request.form.get("PersonEmailAddress")
    return render_template("Login/RegisteredUserUsernamePassword.html")
@app.route("/RegisteredUserUsernamePassword", methods = ["GET", "POST"])
def RegisteredUserUsernamePassword():
    PersonUserName = request.form.get("UserName")
    if db.query(Persons).filter_by(PersonUserName = PersonUserName).first():
        return render_template("Login/LoginFailed.html", message = "Uporabnik s tem imenom že obstaja.", Link="/RegisteredUser")
    else:
        PersonPassword = request.form.get("Password")
        PersonPasswordCofirm = request.form.get("PasswordConfirm")
        if PersonPassword == PersonPasswordCofirm:
            HashedPassword = hashlib.sha256(PersonPassword.encode()).hexdigest()
            person = Persons(PersonName = session["PersonName"],
                             PersonLastName = session["PersonLastName"],
                             PersonEMSO = session["PersonEMSO"],
                             PersonCountry = session["PersonCountry"],
                             PersonEmailAddress = session["PersonEmailAddress"],
                             DateInserted = datetime.now(),
                             PersonUserName = PersonUserName,
                             PersonPassword = HashedPassword,
                             PriorityType = 2,
                             IsDeleted = 0)
            db.add(person)
            db.commit()
            # Napiši funkcijo za pošljanje podatkov na mail.
            return render_template("Login/RegisteredUser.html",
                                   PersonUserName = PersonUserName,
                                   PersonPassword = PersonPassword)
        else:
            return render_template("Login/LoginFailed.html", message = "Gesli se ne ujemata.", Link="/RegisteredUser")
@app.route("/AddHelicopter")
def AddHelicopter():
    return render_template("Admin/AddHelicopter.html")
@app.route("/DeleteHelicopter")
def DeleteHelicopter():
    helikopterji = db.query(Helicopter).filter_by(IsDeleted = 0).all()
    return render_template("Admin/DeleteHelicopter.html", data = helikopterji)
@app.route("/ShowListOfHelicopters")
def ShowListOfHelicopters():
    helikopterji = db.query(Helicopter).filter_by(IsDeleted = 0).all()
    userPriority = db.query(Persons.PriorityType).filter_by(SessionToken = request.cookies.get("session_token")).first()
    if userPriority.PriorityType == 1:
        return render_template("Admin/ShowListOfHelicopters.html", dataHelikopterji=helikopterji)
    else:
        return render_template("User/UserShowListOfHelicopters.html", dataHelikopterji=helikopterji)
@app.route("/RentHelicopter")
def RentHelicopter():
    DataHelikopterji = db.query(Helicopter).filter_by(IsDeleted = 0, Rented = 0).all()
    DataOsebe = db.query(Persons).filter_by(PriorityType = 2).all()
    userPriority = db.query(Persons.PriorityType).filter_by(SessionToken=request.cookies.get("session_token")).first()
    if userPriority.PriorityType == 1:
        return render_template("Admin/RentHelicopter.html",
                               DataHelikopterji = DataHelikopterji,
                               DataOsebe = DataOsebe)
    else:
        return render_template("User/UserRentHelicopter.html", DataHelikopterji = DataHelikopterji)
@app.route("/RentedHelicopter", methods = ["POST"])
def RentedHelicopter():
    HelicopterID = request.form.get("Helicopter")
    helikopter = db.query(Helicopter).get(HelicopterID)
    helikopter.Rented = 1
    PersonID = request.form.get("Person")
    if not PersonID:
        PersonID = db.query(Persons.ID).filter_by(SessionToken = request.cookies.get("session_token")).first().ID
    izposoja = Izposoje(DatumIzposoje = datetime.now(),
                        IDModela = HelicopterID,
                        IDCloveka = PersonID,
                        IsReturned = 0)
    db.add(izposoja)
    db.session.commit()
    return render_template("AdminAndUser/IsRented.html")
@app.route("/ReturnedHelicopter",methods = ["POST"])
def ReturnedHelicopter():
    HelicopterID = request.form.get("Helicopter")
    helikopter = db.query(Helicopter).get(HelicopterID)
    helikopter.Rented = 0
    izposoja = db.query(Izposoje).filter_by(IsReturned = 0, IDModela = HelicopterID).first()
    izposoja.DatumVrnitve = datetime.now()
    izposoja.IsReturned = 1
    db.session.commit()
    return render_template("AdminAndUser/ReturnedHelicopter.html")
@app.route("/ReturnHelicopter")
def ReturnHelicopter():
    userPriority = db.query(Persons.PriorityType).filter_by(SessionToken=request.cookies.get("session_token")).first()
    HelicoptersByUser = db.query(Helicopter.ID, Helicopter.Ime).join(Izposoje, Helicopter.ID == Izposoje.IDModela).filter_by(IsReturned=0)
    if userPriority.PriorityType == 1:
        HelicoptersByUser = HelicoptersByUser.all()
        return render_template("Admin/ReturnHelicopter.html", DataIzposoje = HelicoptersByUser)
    else:
        PersonID = db.query(Persons.ID).filter_by(SessionToken=request.cookies.get("session_token")).first().ID
        HelicoptersByUser = HelicoptersByUser.filter_by(IDCloveka = PersonID).all()
        return render_template("User/UserReturnHelicopter.html", DataIzposoje = HelicoptersByUser)
@app.route("/AddedHelicopter", methods = ["POST"])
def AddedHelicopter():
    HelicopterName = request.form.get("HelicopterName")
    HelicopterModel = request.form.get("HelicopterModel")
    HelicopterYear = request.form.get("HelicopterYear")
    HelicopterPrice = request.form.get("HelicopterPrice")
    helicopter = Helicopter(Ime = HelicopterName,
                            Model = HelicopterModel,
                            LetoIzdelave = datetime.strptime(HelicopterYear, '%Y-%m-%d'),
                            Cena = HelicopterPrice,
                            Rented = 0,
                            IsDeleted = 0)
    db.add(helicopter)
    db.commit()
    return render_template("Admin/AddedHelicopter.html")
@app.route("/DeletedHelicopter", methods = ["POST"])
def DeletedHelicopter():
    HelicopterID = request.form.get("HelicopterDelete")
    helikopter = db.query(Helicopter).get(HelicopterID)
    helikopter.IsDeleted = 1
    db.session.commit()
    return render_template("Admin/DeletedHelicopter.html")
@app.route("/Admin/Users", methods=["GET"])
def GetAllUsers():
    users = db.query(Persons).filter_by(PriorityType = 2).all()
    return render_template("Admin/ShowListOfUsers.html", users = users)
@app.route("/Admin/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(Persons).get(int(user_id))
    session["ID"] = user.ID
    HelicoptersByUser = db.query(Helicopter, Izposoje).join(Izposoje, Helicopter.ID == Izposoje.IDModela).filter_by(IDCloveka = user_id).all()
    return render_template("Admin/UserDetails.html",
                           user = user,
                           HelicoptersData = HelicoptersByUser)
@app.route("/Profile")
def Profile():
    user = db.query(Persons).filter_by(SessionToken = request.cookies.get("session_token")).first()
    return render_template("User/Profile.html", user = user)
@app.route("/Profile/Edit", methods = ["GET", "POST"])
def ProfileEdit():
    session_token = request.cookies.get("session_token")
    user = db.query(Persons).filter_by(SessionToken = session_token).first()
    if request.method == "GET":
        return render_template("User/ProfileEdit.html", user = user)
    elif request.method == "POST":
        user.PersonName = request.form.get("profile-name")
        user.PersonLastName = request.form.get("profile-lastname")
        user.PersonEMSO = request.form.get("profile-emso")
        user.PersonCountry = request.form.get("profile-country")
        user.PersonEmailAddress = request.form.get("profile-email")
        user.DateModified = datetime.now()
        db.add(user)
        db.commit()
        return redirect(url_for("Profile"))
@app.route("/Profile/ChangePassword")
def profile_change_password():
    session_token = request.cookies.get("session_token")
    user = db.query(Persons).filter_by(SessionToken = session_token).first()
    return render_template("User/ChangePassword.html", user = user)
@app.route("/Profile/ChangedPassword", methods=["POST"])
def profile_changed_password():
    session_token = request.cookies.get("session_token")
    user = db.query(Persons).filter_by(SessionToken = session_token).first()
    if request.method == "POST":
        OldPassword = request.form.get("profile-OldPassword")
        NewPassword = request.form.get("profile-NewPassword")
        ConfirmNewPassword = request.form.get("profile-ConfirmNewPassword")
        hashed_old_password = hashlib.sha256(OldPassword.encode()).hexdigest()
        if hashed_old_password != user.PersonPassword:
            return render_template("User/ChangedPassword.html", message = "Napačno geslo poskusi znova.", Link="/Profile/ChangePassword")
        elif hashed_old_password == user.PersonPassword:
            hashed_new_password = hashlib.sha256(NewPassword.encode()).hexdigest()
            hashed_confirm_new_password = hashlib.sha256(ConfirmNewPassword.encode()).hexdigest()
            if hashed_new_password == hashed_confirm_new_password:
                user.PersonPassword = hashed_new_password
                db.add(user)
                db.commit()
                return render_template("User/ChangedPassword.html", message="Geslo je bilo uspešno spremenjeno.", Link="/Profile")
            else:
                return render_template("User/ChangedPassword.html", message = "Napačni novi gesli izberi znova.", Link="/Profile/ChangePassword")
@app.route("/Profile/Delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")
    user = db.query(Persons).filter_by(SessionToken = session_token).first()
    if request.method == "GET":
        return render_template("User/ProfileDelete.html", user = user)
    elif request.method == "POST":
        user.IsDeleted = 1
        db.add(user)
        db.commit()
        return redirect(url_for("LoginForm"))
@app.route("/Admin/RebuildProfile")
def RebuildProfile():
    user = db.query(Persons).get(session["ID"])
    user.IsDeleted = 0
    db.add(user)
    db.commit()
    return redirect(url_for("user_details", user_id = user.ID))
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()