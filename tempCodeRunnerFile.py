from flask import Flask, redirect, render_template, request, flash, json,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user,encode_cookie
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from sqlalchemy import text







app = Flask(__name__)
app.secret_key = "praneethvarma"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/covid'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



login_manager = LoginManager(app)
login_manager.login_view = 'login'



with open(r'project\config.json', 'r') as c:
    params = json.load(c)["params"]
    
    
    


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)
    
    
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




class test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    
    
#local data base ki link avutadi user table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50))
    dob = db.Column(db.String(1000))
    
    
    
#local data base ki link avutadi table addhospitadata ki
class Hospitaluser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(1000))
    
    
    
#HOSPITAL DATA KI local data base ki connection
class Hospitaldata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True)
    hname = db.Column(db.String(100))
    normalbed = db.Column(db.Integer)
    hicubed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    vbed = db.Column(db.Integer)
    
    
    #class dinikil
class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    bedtype=db.Column(db.String(100))
    hcode=db.Column(db.String(20))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(100))
    pphone=db.Column(db.String(100))
    paddress=db.Column(db.String(100))  
    
    
    
#contact ki class 
class Contact:
    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

    def send_email(self):
        # Implement email sending logic here
        pass

    def Contact(self):
        # Implement database saving logic here
        pass

    
    

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")



@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")




@app.route('/signup', methods=['POST'])
def signup():
    if request.method == "POST":
        srfid = request.form.get('srf')
        email = request.form.get('email')
        dob = request.form.get('dob')

        if not srfid or not email or not dob:
            flash("Please fill in all the fields", "warning")
            return render_template("usersignup.html")

        existing_srfid_user = User.query.filter_by(srfid=srfid).first()
        existing_email_user = User.query.filter_by(email=email).first()
        if existing_srfid_user or existing_email_user:
            flash("SRF ID or Email ID is already taken", "warning")
            return render_template("usersignup.html")

        if dob:
            dob_hash = generate_password_hash(dob)
        else:
            return "DOB is empty!"

        new_user = User(srfid=srfid, email=email, dob=dob_hash)
        db.session.add(new_user)
        db.session.commit()

        print(f"User added: srfid - {srfid}, email - {email}, dob - {dob}")
        flash("Sign up success. Please login.", "success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")






# login page ki idi

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        srfid = request.form.get('srf')
        dob = request.form.get('dob')
        user = User.query.filter_by(srfid=srfid).first()
      
        if user:
            if check_password_hash(user.dob, dob):
                login_user(user) 
                flash("login successful", "info")
                return render_template("index.html")
            else:
                flash("invalid credentials", "danger")
                return render_template("userlogin.html")
        else:
            flash("no user found", "danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/login')


# admin page ki access

@app.route('/admin', methods=['POST', 'GET'])
def admin_login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if (username == params['user'] and password == params['password']):
            session['user'] = username
            flash("Login success", "info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid credentials", "danger")
    return render_template("admin.html")




@app.route('/logoutadmin')
def logoutadmin():
    session.pop('user')
    flash('You have been logged out admin.', 'info')
    return render_template("admin.html")






# mail ki aa credentials vellaka login avataniki

@app.route('/hospitallogin', methods=['POST', 'GET'])
def hospitallogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = Hospitaluser.query.filter_by(email=email).first()
      
        if user:
            if check_password_hash(user.password, password):
                login_user(user) 
                flash("login successful", "info")
                return render_template("index.html")
            else:
                flash("invalid credentials", "danger")
                return render_template("hospitallogin.html")
        else:
            flash("no user found", "danger")
            return render_template("hospitallogin.html")

    return render_template("hospitallogin.html")








@app.route('/addHospitalUser', methods=['POST', 'GET'])
def hospitalUser():
    if 'user' in session and session['user'] == params['user']:
        if request.method == "POST":
            hcode = request.form.get('hcode')
            email = request.form.get('email')
            password = request.form.get('password')        
            encpassword = generate_password_hash(password)
            emailUser = Hospitaluser.query.filter_by(email=email).first()
            hcode=hcode.upper()
            if emailUser:
                flash("Email or hcode is already taken", "warning")
                return render_template("addHosUser.html")

            # Execute raw SQL query to insert data into the hospitaluser table
            insert_query = text("INSERT INTO `hospitaluser` (`hcode`, `email`, `password`) VALUES (:hcode, :email, :encpassword)")
            db.session.execute(insert_query, {"hcode": hcode, "email": email, "encpassword": encpassword})
            db.session.commit()

            # Send email
            mail.send_message('COVID CARE CENTER', sender=params['gmail-user'], recipients=[email], body=f"Welcome thanks for choosing us\nYour Login Credentials Are:\nEmail Address: {email}\nPassword: {password}\n\n Hospital Code {hcode}\n\n Hospital code {hcode}\n Do not share your password\n\n\nThank You...")

            flash("Data Sent and Inserted Successfully", "success")
            return render_template("addHosUser.html")
    else:
        flash("Login and try again", "warning")
    return render_template("admin.html")




#data add cheyadasniki hos user ki

@app.route("/addhospitalinfo", methods=['POST', 'GET']) 
def addhospitalinfo():
    if request.method == "POST":
        hcode = request.form.get('hcode')
        hname = request.form.get('hname')
        nbed = request.form.get('normalbed')
        hbed = request.form.get('hicubeds')
        ibed = request.form.get('icubeds')
        vbed = request.form.get('ventbeds')
        hcode = hcode.upper()
        huser = Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("data is already present , if any changes ,pls contact admin")
            return render_template("hospitaldata.html")
        if huser:
            query = text("INSERT INTO hospitaldata (hcode, hname, normalbed, hicubed, icubed, vbed) VALUES (:hcode, :hname, :nbed, :hbed, :ibed, :vbed)")
            db.session.execute(query, {"hcode": hcode, "hname": hname, "nbed": nbed, "hbed": hbed, "ibed": ibed, "vbed": vbed})
            db.session.commit()
            flash("Data is added", "primary")
        else:
            flash("Hospital code not found", "warning")
    
    return render_template("hospitaldata.html")







#details ni edit cheyadaniki
@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
  
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        # db.engine.execute(f"UPDATE `hospitaldata` SET `hcode` ='{hcode}',`hname`='{hname}',`normalbed`='{nbed}',`hicubed`='{hbed}',`icubed`='{ibed}',`vbed`='{vbed}' WHERE `hospitaldata`.`id`={id}")
        post=Hospitaldata.query.filter_by(id=id).first()
        post.hcode=hcode
        post.hname=hname
        post.normalbed=nbed
        post.hicubed=hbed
        post.icubed=ibed
        post.vbed=vbed
        db.session.commit()
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    # posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html",posts=posts)






#pateint detail home page lodi
@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.srfid
    print(code)
    data=Bookingpatient.query.filter_by(srfid=code).first()
    return render_template("details.html",data=data)



#contact avadaniki
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        
        return "Form submitted successfully!"
    else:
        return render_template("contact.html")










@app.route("/slotbooking", methods=['POST', 'GET'])
@login_required
def slotbooking():
    query1 = Hospitaldata.query.all()
    query = Hospitaldata.query.all()
    if request.method == "POST":
        srfid = request.form.get('srfid')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')
        check2 = Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient = Bookingpatient.query.filter_by(srfid=srfid).first()
        if checkpatient:
            flash("already srd id is registered ", "warning")
            return render_template("booking.html", query=query, query1=query1)

        if not check2:
            flash("Hospital Code not exist", "warning")
            return render_template("booking.html", query=query, query1=query1)

        code = hcode
        dbb = Hospitaldata.query.filter_by(hcode=hcode).first()
        seat = None  
        if bedtype == "NormalBed":
            seat = dbb.normalbed
        elif bedtype == "HICUBed":
            seat = dbb.hicubed
        elif bedtype == "ICUBed":
            seat = dbb.icubed
        elif bedtype == "VENTILATORBed":
            seat = dbb.vbed

        if seat is not None:  
            if seat > 0:
                ar = Hospitaldata.query.filter_by(hcode=code).first()
                setattr(ar, bedtype.lower(), seat - 1)
                db.session.commit()
                res = Bookingpatient(srfid=srfid, bedtype=bedtype, hcode=hcode, spo2=spo2, pname=pname, pphone=pphone, paddress=paddress)
                db.session.add(res)
                db.session.commit()
                flash("Slot is Booked kindly Visit Hospital for Further Procedure", "success")
                return render_template("booking.html", query=query, query1=query1)
            else:
                flash("No available beds of this type", "danger")
        else:
            flash("Invalid bed type", "danger")

    return render_template("booking.html", query=query, query1=query1)










 

# checking whether db is connected or not
@app.route("/check")
def check():
    try:
        a=test.query.all()
        print(a)
        return f'My database is connected '
    except Exception as e:
        print(e)
        return 'My database is not connected'
   

    
   
   
   
if __name__ == '__main__':
    app.run(debug=True)