from os import name
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import re
import pymysql
from pymysql import cursors
import json
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/upload/car' 
UPLOAD_USER = 'static/upload/user' 

app = Flask(__name__)
app.secret_key = 'qwertyuiop[]1=2-30495867'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_USER'] = UPLOAD_USER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def getConnection ():
    return pymysql.connect(
        host = 'localhost',
        db = 'seproject',
        user = 'root',
        password = '',
        charset = 'utf8',
        cursorclass = pymysql.cursors.DictCursor
		)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
def makecar():
    connection = getConnection()
    sql = "SELECT make FROM vehiclemodelyear GROUP BY make"
    cursor = connection.cursor()
    cursor.execute(sql)
    make = cursor.fetchall()
    return make

def yearcar():
    connection = getConnection()
    sql = "SELECT year FROM vehiclemodelyear GROUP BY year"
    cursor = connection.cursor()
    cursor.execute(sql)
    yea = cursor.fetchall()
    return yea

def province():
    connection = getConnection()
    sql = "SELECT name_th FROM provinces ORDER BY name_th"
    cursor = connection.cursor()
    cursor.execute(sql)
    pro = cursor.fetchall()
    return pro

def vehiclemodelyear():
    connection = getConnection()
    sql = "SELECT DISTINCT model,make FROM vehiclemodelyear "
    cursor = connection.cursor()
    cursor.execute(sql)
    veh = cursor.fetchall()
    data = dict()
    for i in veh:
        if i['make'] in data:
            data[i['make']].append(i['model'])
            data[i['make']].sort()
        else:
            data[i['make']] = [i['model']]
    # print(data)
    return data 

def showcar():
    connection = getConnection()
    sql = "SELECT s.iduser,s.Id_car,u.occupation,s.make,s.model,s.year,s.province,s.detail,s.sell_status,s.price,s.imgcar_1,s.imgcar_2,s.imgcar_3,s.imgcar_4,u.Name,u.Lastname,u.Email,u.Phone FROM sell_car as s , user as u  WHERE s.iduser = u.Id"
    cursor = connection.cursor()
    cursor.execute(sql)
    show = cursor.fetchall()
    return show
    
@app.route('/')
def index():
   connection = getConnection()
   sql = "SELECT * FROM sell_car ORDER BY RAND() LIMIT 4;"
   cursor = connection.cursor()
   cursor.execute(sql)
   car = cursor.fetchall()
   return render_template('index.html',car=car)

@app.route('/buycar')
def buycar():
   car = showcar()
   return render_template('buycar.html',car=car)

@app.route('/buycaruser')
def buycaruser():
   car = showcar()
   return render_template('buycaruser.html',name=session['name'],car=car)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if email == "admin@admin.com":
            connection = getConnection()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
            user = cursor.fetchone()
            if user:
                session['loggedin'] = True
                session['id'] = user['Id']
                session['name'] = user['Name']
                session['lastname'] = user['Lastname']
                session['email'] = user['Email']
                session['address'] = user['address']
                session['Phone'] = user['Phone']
                session['occupation'] = user['occupation']
                session['ctzid'] = user['ctzid']
                session['password'] = user['Password']
                session['imguser'] = user['imguser']
                return redirect(url_for('index'))
        elif user:
            session['loggedin'] = True
            session['id'] = user['Id']
            session['name'] = user['Name']
            session['lastname'] = user['Lastname']
            session['email'] = user['Email']
            session['address'] = user['address']
            session['Phone'] = user['Phone']
            session['occupation'] = user['occupation']
            session['ctzid'] = user['ctzid']
            session['password'] = user['Password']
            session['imguser'] = user['imguser']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect E-mail/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   session.pop('name', None)
   session.pop('lastname', None)
   session.pop('address', None)
   session.pop('Phone', None)
   session.pop('occupation', None)
   session.pop('ctzid', None)
   session.pop('password', None)
   session.pop('imguser', None)
   return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form and 'ctzid' in request.form and 'phone' in request.form:
        name = request.form['name']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        ctzid = request.form['ctzid']
        phone = request.form['phone']
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM user WHERE name = %s AND Email = %s', (name,email,))
        user = cursor.fetchone()
        if user:
            msg = 'User already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            connection = getConnection()
            cursor = connection.cursor()
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, lastname, email, password, ctzid, 'ยังไม่ระบุ', phone, 'ยังไม่ระบุ', 'none.png'))
            connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('login.html', msg=msg)

@app.route('/home')
def home():
    n = session['name']
    if 'loggedin' in session:
        connection = getConnection()
        sql = "SELECT * FROM sell_car ORDER BY RAND() LIMIT 4;"
        cursor = connection.cursor()
        cursor.execute(sql)
        car = cursor.fetchall()
        return render_template('indexuser.html',name=session['name'], lastname=session['lastname'], ids=session['id'], email=session['email'], address=session['address'], Phone=session['Phone'],occupation=session['occupation'],password=session['password'],ctzid=session['ctzid'],imguser=session['imguser'],n=n,car=car)  

    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        print(session['imguser'])
        return render_template('profile.html',name=session['name'], lastname=session['lastname'], ids=session['id'], email=session['email'], address=session['address'], Phone=session['Phone'], occupation=session['occupation'],password=session['password'],ctzid=session['ctzid'],imguser=session['imguser'])   

@app.route('/editprofile', methods=['POST', 'GET'])
def editprofile():
   ids = request.form['ids']
   name = request.form['name']
   lastname = request.form['lastname']
   address = request.form['address']
   occupation = request.form['occupation']
   email = request.form['email']
   Phone = request.form['Phone']
   ctzid = request.form['ctzid']
   password = request.form['password']
   imguser = request.form['imguser']
   return render_template('editprofile.html', ids=ids,name= name, lastname=lastname, address=address, occupation=occupation, email=email,Phone=Phone,ctzid=ctzid,password=password,imguser=imguser)

@app.route('/insertuser',methods = ['POST', 'GET'])
def insertuser():
    file = request.files['file']
    nameimg = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_USER'], nameimg))
    ids = request.form['ids']
    n = request.form['name']
    l = request.form['lastname']
    p = request.form['Phone']
    e = request.form['email']
    a = request.form['address']
    o = request.form['occupation']
    c = request.form['ctzid']
    pa = request.form['password']
    connection = getConnection()
    sql = f"UPDATE user SET Name = '{n}', Lastname ='{l}', Email='{e}', Password='{pa}', ctzid = '{c}', address='{a}', Phone='{p}', occupation='{o}', imguser='{nameimg}' WHERE Id = '{ids}'"
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    return login()

@app.route('/uploadcar')
def uploadcar():
   veh = vehiclemodelyear()
   make = [x for x in veh.keys()]
   make.sort()
   yea = yearcar()
   pro = province()
   return render_template('uploadcar.html',name=session['name'],ids=session['id'],Phone=session['Phone'],veh=veh, make=make, yea=yea,pro=pro)

@app.route('/promotion')
def promotion():
   return render_template('promotion.html')

@app.route('/promotionuser')
def promotionuser():
   return render_template('promotionuser.html',name=session['name'])

@app.route('/search')
def search():
   veh = vehiclemodelyear()
   make = [x for x in veh.keys()]
   make.sort()
   yea = yearcar()
   pro = province()
   return render_template('search.html',veh=veh, make=make, yea=yea,pro=pro)

@app.route('/searchuser')
def searchuser():
   veh = vehiclemodelyear()
   make = [x for x in veh.keys()]
   make.sort()
   yea = yearcar()
   pro = province()
   return render_template('searchuser.html',veh=veh, make=make, yea=yea,pro=pro,name=session['name'])

@app.route('/searchcar', methods=['GET', 'POST'])
def searchcar():
    make = request.form['make']
    model = request.form['model']
    province = request.form['province']
    minprice = request.form['minprice']
    maxprice = request.form['maxprice']
    connection = getConnection()
    cursor = connection.cursor()
    sql = f"SELECT s.iduser,s.Id_car,u.occupation,s.make,s.model,s.year,s.province,s.detail,s.sell_status,s.price,s.imgcar_1,s.imgcar_2,s.imgcar_3,s.imgcar_4,u.Name,u.Lastname,u.Email,u.Phone FROM sell_car as s , user as u  WHERE s.iduser = u.Id AND make LIKE '{make}' AND model LIKE '{model}' AND province LIKE '{province}' AND price BETWEEN '{minprice}' AND '{maxprice}'"
    #sql = f"SELECT * FROM sell_car WHERE make LIKE '{make}' AND model LIKE '{model}' AND province LIKE '{province}' AND price BETWEEN '{minprice}' AND '{maxprice}' "
    cursor = connection.cursor()
    cursor.execute(sql)
    car = cursor.fetchall()
    return render_template('buycar.html', car=car)

@app.route('/searchcaruser', methods=['GET', 'POST'])
def searchcaruser():
    make = request.form['make']
    model = request.form['model']
    province = request.form['province']
    minprice = request.form['minprice']
    maxprice = request.form['maxprice']
    connection = getConnection()
    cursor = connection.cursor()
    sql = f"SELECT s.iduser,s.Id_car,u.occupation,s.make,s.model,s.year,s.province,s.detail,s.sell_status,s.price,s.imgcar_1,s.imgcar_2,s.imgcar_3,s.imgcar_4,u.Name,u.Lastname,u.Email,u.Phone FROM sell_car as s , user as u  WHERE s.iduser = u.Id AND make LIKE '{make}' AND model LIKE '{model}' AND province LIKE '{province}' AND price BETWEEN '{minprice}' AND '{maxprice}'"
    #sql = f"SELECT * FROM sell_car WHERE make LIKE '{make}' AND model LIKE '{model}' AND province LIKE '{province}' AND price BETWEEN '{minprice}' AND '{maxprice}' "
    cursor = connection.cursor()
    cursor.execute(sql)
    car = cursor.fetchall()
    return render_template('buycaruser.html', car=car, name=session['name'])

@app.route('/insertcar',methods = ['POST', 'GET'])
def insertcar():
    file1 = request.files['file1']
    file2 = request.files['file2']
    file3 = request.files['file3']
    file4 = request.files['file4']
    filename1 = secure_filename(file1.filename)
    filename2 = secure_filename(file2.filename)
    filename3 = secure_filename(file3.filename)
    filename4 = secure_filename(file4.filename)
    file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
    file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
    file4.save(os.path.join(app.config['UPLOAD_FOLDER'], filename4))
    make = request.form['make']
    iduser = request.form['ids']
    model = request.form['model']
    province = request.form['province']
    detail = request.form['detail']
    price = request.form['price']
    year = request.form['year']
    imgcar_1 = secure_filename(file1.filename)
    imgcar_2 = secure_filename(file2.filename)
    imgcar_3 = secure_filename(file3.filename)
    imgcar_4 = secure_filename(file4.filename)
    connection = getConnection()
    sql1 = "INSERT INTO sell_car(iduser,make, model, year, province, detail,sell_status,price,imgcar_1,imgcar_2,imgcar_3,imgcar_4) VALUES('%s','%s', '%s', '%s', '%s', '%s','ยังขายไม่ออก', '%s', '%s', '%s', '%s','%s')" % (iduser,make, model, year,province,detail,price,imgcar_1,imgcar_2,imgcar_3,imgcar_4)
    cursor = connection.cursor()
    cursor.execute(sql1)
    connection.commit()
    return home()


@app.route('/detailcar', methods=['POST', 'GET'])
def detailcar():
   make = request.form['make']
   model = request.form['model']
   price = request.form['price']
   year = request.form['year']
   province = request.form['province']
   detail = request.form['detail']
   sell_status = request.form['sell_status']
   imgcar_1 = request.form['imgcar_1']
   imgcar_2 = request.form['imgcar_2']
   imgcar_3 = request.form['imgcar_3']
   imgcar_4 = request.form['imgcar_4']
   Name = request.form['Name']
   Lastname = request.form['Lastname']
   Email = request.form['Email']
   Phone = request.form['Phone']
   iduser = request.form['iduser']
   idscar  = request.form['idscar']
   occupation  = request.form['occupation']
   connection = getConnection()
   sql = f"SELECT * FROM comment WHERE Id_car = '{idscar}' "
   cursor = connection.cursor()
   cursor.execute(sql)
   com = cursor.fetchall()
   return render_template('detailcar.html',occupation=occupation,com=com,iduser=iduser,idscar=idscar,make=make,model=model,price=price,year=year,province=province,detail=detail,sell_status=sell_status,Name=Name,Lastname=Lastname,Email=Email,Phone=Phone,imgcar_1=imgcar_1,imgcar_2=imgcar_2,imgcar_3=imgcar_3,imgcar_4=imgcar_4)


@app.route('/detailcaruser', methods=['POST', 'GET'])
def detailcaruser():
   make = request.form['make']
   model = request.form['model']
   price = request.form['price']
   year = request.form['year']
   province = request.form['province']
   detail = request.form['detail']
   sell_status = request.form['sell_status']
   imgcar_1 = request.form['imgcar_1']
   imgcar_2 = request.form['imgcar_2']
   imgcar_3 = request.form['imgcar_3']
   imgcar_4 = request.form['imgcar_4']
   Name = request.form['Name']
   Lastname = request.form['Lastname']
   Email = request.form['Email']
   Phone = request.form['Phone']
   #iduser = request.form['iduser']
   idscar  = request.form['idscar']
   connection = getConnection()
   sql = f"SELECT * FROM comment WHERE Id_car = '{idscar}' "
   cursor = connection.cursor()
   cursor.execute(sql)
   com = cursor.fetchall()
   return render_template('detailcaruser.html',occupation=session['occupation'],iduser=session['id'],lastname=session['lastname'],com=com,name=session['name'],img=session['imguser'],idscar=idscar,make=make,model=model,price=price,year=year,province=province,detail=detail,sell_status=sell_status,Name=Name,Lastname=Lastname,Email=Email,Phone=Phone,imgcar_1=imgcar_1,imgcar_2=imgcar_2,imgcar_3=imgcar_3,imgcar_4=imgcar_4)

@app.route('/comments', methods=['POST', 'GET'])
def comments():
   idscar = request.form['idscar']
   iduser = request.form['iduser']
   Name = request.form['name']
   Lastname = request.form['lastname']
   comment = request.form['comment']
   occupation = request.form['occupation']
   connection = getConnection()
   sql1 = "INSERT INTO comment(Id_car,Id_user, Name, Lastname, occupation, comment) VALUES('%s','%s', '%s', '%s', '%s', '%s')" % (idscar,iduser, Name, Lastname,comment,occupation)
   cursor = connection.cursor()
   cursor.execute(sql1)
   connection.commit()
   return home()

@app.route('/listcar', methods=['POST', 'GET'])
def listcar():
   ids = session['id']
   connection = getConnection()
   sql = f"SELECT * FROM sell_car WHERE iduser = '{ids}'"
   cursor = connection.cursor()
   cursor.execute(sql)
   listcar = cursor.fetchall()
   sql1 = f"SELECT s.iduser,s.Id_car,u.occupation,s.make,s.model,s.year,s.province,s.detail,s.sell_status,s.price,s.imgcar_1,s.imgcar_2,s.imgcar_3,s.imgcar_4,u.Name,u.Lastname,u.Email,u.Phone FROM sell_car as s , user as u, favorite_car as f  WHERE  f.Id_user ='{ids}' AND f.Id_car = s.Id_car AND s.iduser = u.Id"
   cursor = connection.cursor()
   cursor.execute(sql1)
   car = cursor.fetchall()
   return render_template('listcar.html',listcar=listcar,name=session['name'],car=car)

@app.route('/editcar', methods=['POST', 'GET'])
def editcar():
   Id_car  = request.form['Id_car']
   make  = request.form['make']
   model  = request.form['model']
   price  = request.form['price']
   detail  = request.form['detail']
   sell_status  = request.form['sell_status']
   return render_template('editcar.html',Id_car=Id_car,make=make,model=model,price=price,detail=detail,sell_status=sell_status,name=session['name'])

@app.route('/savecar', methods=['POST', 'GET'])
def savecar():
   Id_car  = request.form['Id_car']
   price  = request.form['price']
   detail  = request.form['detail']
   sell_status  = request.form['sell_status']
   connection = getConnection()
   sql = f"UPDATE sell_car SET price = '{price}', detail ='{detail}', sell_status='{sell_status}' WHERE Id_car  = '{Id_car}'"
   cursor = connection.cursor()
   cursor.execute(sql)
   connection.commit()
   return home()

@app.route('/favorite', methods=['POST', 'GET'])
def favorite():
   idscar  = request.form['idscar']
   iduser  = request.form['iduser']
   connection = getConnection()
   sql = "INSERT INTO favorite_car(Id_car,Id_user) VALUES('%s','%s')" % (idscar,iduser)
   cursor = connection.cursor()
   cursor.execute(sql)
   connection.commit()
   return home()

if __name__ == '__main__':
   app.run(debug = True)