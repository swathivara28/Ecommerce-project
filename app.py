from flask import Flask,redirect,render_template,url_for,session,request,flash

from database import createTables,AuthQueries
import bcrypt
app = Flask(__name__)

app.secret_key = "Swathi@1234"

#======================================
#       Authentication Routes
#======================================
# home route
@app.route('/')
def home():
    return render_template('home.html')
   
# register route
@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # check password and confirm_password both same or not
        if password != confirm_password:
            print('Password missmatch', 'err')
            return redirect('/register')

        # check email exist or not
        status, user = AuthQueries.getUserData(email=email)
        if status == True:
            flash("Email Already Exists",'err')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash("Password Miss Match",'err')
            return redirect(url_for('register'))
        
        # generate hashpassword
        hash_password = bcrypt.hashpw(password=password.encode('utf-8'),
                                      salt = bcrypt.gensalt(4))
        
        # insert user data into users table
        status,msg = AuthQueries.createUserAccount(name=name,
                                                  email=email,
                                                  password=hash_password,
                                                  phone=phone)
        if status == False:
            flash(msg,'err')
            return redirect(url_for('register'))
        flash (msg,'msg')
        return redirect(url_for('login'))
        

# login route
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # check email exists or not
        status, user = AuthQueries.getUserData(email=email)
        if status == False:
            flash(user,'err')
            return redirect('/login')
                
        #verify hashpassword
        verify_password_status = bcrypt.checkpw(password=password.encode('utf-8'),
                                hashed_password=user['hashpassword'].encode('utf-8'))
    
        if  verify_password_status == False:
            flash('Password incorrect','err')
            return redirect('/login')
        # store user data in session
        
        session['username'] = user['username']
        session['role'] = user['role']
        session['id'] = user['userid']
        session['email'] = user['email']
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('products'))


    
# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", 'msg')
    return redirect(url_for('login'))



#========================================================
#                   User Routes
#========================================================
@app.route('/products')
def products():
    return "User Dashboard"



#========================================================
#                   Admin Routes
#========================================================
@app.route('/admin/dashboard')
def admin_dashboard():
    return "Admin Dashboard"




# main
if __name__=="__main__":
    print(createTables())
    app.run(debug=True)