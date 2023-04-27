from flask import Flask,request,redirect,render_template,url_for,flash,session
from flask_session import Session
from otp import genotp
from cmail import sendmail
from tokenreset import token
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import os
from io import BytesIO
import mysql.connector
app=Flask(__name__)
app.secret_key='admin@123'
app.config['SESSION_TYPE']='filesystem'

db=os.environ['RDS_DB_NAME']
user=os.environ['RDS_USERNAME']
password=os.environ['RDS_PASSWORD']
host=os.environ['RDS_HOSTNAME']
port=os.environ['RDS_PORT']
mydb=mysql.connector.connect(host=host,user=user,password=password,db=db,port=port)
#mydb=mysql.connector.connect(host='localhost',user='root',password='Eswar@2001',db='spm')
with mysql.connector.connect(host=host,user=user,password=password,db=db,port=port) as conn:
    cursor=conn.cursor()
    cursor.execute("create table if not exists students(user varchar(30) primary key,email varchar(30),password varchar(10),ccode varchar(10))")
    cursor.execute("create table if not exists addstu(studentid varchar(10) primary key,studentname varchar(10),section varchar(20),mobile bigint unique,Address varchar(50),Department varchar(20))")
    cursor.execute("create table if not exists addsub(courseid varchar(20)primary key,coursetitle varchar(20),maxmarks bigint)")
    cursor.execute("create table if not exists internalresults(studentid varchar(10),courseid varchar(20),Internal1 enum('Internal1'),Internal2 enum('Internal2'),internalmarks2 smallint,internalmarks1 smallint,section enum('BCA','B.Sc M.S.Ds','BBA','BBA BA','BA','BSC MPCs','B.Sc C.A.M.E','B.Sc M.S.Cs'),foreign key(studentid) references addstu(studentid),foreign key(courseid) references addsub(courseid))")
    cursor.execute("create table if not exists semresults(studentid varchar(10),courseid varchar(20),Semister enum('sem1','sem2','sem3','sem4','sem5','sem6'),Semmarks int,section enum('BCA','B.Sc M.S.Ds','BBA','BBA BA','BA','BSC MPCs','B.Sc C.A.M.E','B.Sc M.S.Cs'),foreign key(studentid) references addstu(studentid),foreign key(courseid) references addsub(courseid))")
    cursor.execute("create table if not exists contactus(name varchar(30),emailid varchar(40),message tinytext)")

Session(app)
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=="POST":
        name=request.form['name']
        emailid=request.form['emailid']
        message=request.form['message']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into contactus(name,emailid,message) values(%s,%s,%s)',[name,emailid,message])
        mydb.commit()
    return render_template('Myresult.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        user=request.form['AdminName']
        Email=request.form['email']
        password=request.form['password']
        ccode=request.form['Ccode']
        code='admin@123'
        if code==code:
            cursor.execute('select user from a_register')
            data=cursor.fetchall()
            if (user,) in data:
                flash('user already exits')
                return render_template('register.html')
            cursor.close()
            if (email,) in data:
                flash('email already exit')
                return render_template('register.html')
            cursor.close()
            otp=genotp()
            subject='Thanks for registering to the application'
            body=f'Use this otp to registre{otp}'
            sendmail(Email,subject,body)
            return render_template('otp.html',otp=otp,user=user,Email=Email,password=password,ccode=ccode)
        else:
            flash('Invaild Secret code')
    return render_template('register.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('dash'))
    if request.method=='POST':
        AdminName=request.form['AdminName']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*)from a_register where user=%s and password=%s',[AdminName,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid user or password')
            return render_template('a_login.html')
        else:
            session['user']=AdminName             #session use to restrick homepage
            return redirect(url_for('dash'))    #linkhome restricked
    return render_template('a_login.html')
@app.route('/dash')
def dash():
    if session.get('user'):
        return render_template('dash.html')
    else:
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))
    else:
        flash('already logged out')
        return redirect(url_for('index'))
        
@app.route('/otp/<otp>/<user>/<Email>/<password>/<ccode>',methods=['GET','POST'])
def otp(otp,user,Email,password,ccode):
    if request.method=='POST':
        uotp=request.form['otp']
        print(otp)
        print(uotp)
        if otp==uotp:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into a_register values(%s,%s,%s,%s)',(user,Email,password,ccode))
            mydb.commit()
            cursor.close()
            flash('Successfully Detail Register')
            return redirect(url_for('login'))
        else:
            flash('Worng otp')
            return render_template('otp.html',otp=otp,user=user,Email=Email,password=password,ccode=ccode)
@app.route('/addstudent',methods=['GET','POST'])
def addstudent():
    if session.get('user'):
        if request.method=='POST':
            studentid=request.form['studentid']
            studentname=request.form['studentname']
            section=request.form['section']
            mobile=request.form['mobile']
            Address=request.form['Address']
            Department=request.form['Department']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into addstu value(%s,%s,%s,%s,%s,%s)',(studentid,studentname,section,mobile,Address,Department))
            cursor.connection.commit()
            flash(f' added successfully')
            return redirect(url_for('dash'))
        return render_template('addstudent.html')
    else:
        return redirect(url_for('login'))
@app.route('/addsubject',methods=['GET','POST'])
def addsubject():
    if session.get('user'):
        if request.method=='POST':
            courseid=request.form['courseid']
            coursetitle=request.form['coursetitle']
            mmark=request.form['mmark']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into addsub value(%s,%s,%s)',(courseid,coursetitle,mmark))
            cursor.connection.commit()
            flash(f' added successfilly')
            return redirect(url_for('dash'))
        return render_template('addsubject.html')
    else:
        return redirect(url_for('login'))
@app.route('/forgot',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        user=request.form['id']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select user from a_register')
        data=cursor.fetchall()
        if(user,)in data:
            cursor.execute('select email from a_register where user=%s',[user])
            data=cursor.fetchone()[0]
            print(data)
            cursor.close()
            subject='Reset Password for {email}'
            body=f'Reset the password using {request.host+url_for("createpassword",token=token(user,200))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user'
    return render_template('Forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
        try:
            s=Serializer(app.config['SECRET_KEY'])
            user=s.loads(token)['user']
            if request.method=='POST':
                npass=request.form['npassword']
                cpass=request.form['cpassword']
                if npass==cpass:
                    cursor=mydb.cursor(buffered=True)
                    cursor.execute('update a_register set password=%s where user=%s',[npass,user])
                    mydb.commit()
                    return 'Password reset Successfull'
                else:
                    return 'Password mismatch'
            return render_template('newpassword.html')
        except Exception as e:
            print(e)
            return 'Link Expired try again'
@app.route('/addsemresult',methods=['GET','POST'])
def addsemresult():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('SELECT studentid from addstu')
        data=cursor.fetchall()
        cursor.execute('SELECT COURSEID FROM addsub')
        cdata=cursor.fetchall()
        if request.method=='POST':
            id1=request.form['id']
            course=request.form['course']
            semt=request.form['semt']
            smarks=request.form['smarks']
            section=request.form['section']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into semresults value(%s,%s,%s,%s,%s)',(id1,course,semt,smarks,section))
            cursor.connection.commit()
            flash(f'added successfilly')
            return redirect(url_for('dash'))
        return render_template('addsemresult.html',data=data,cdata=cdata)
    else:
        return redirect(url_for('login'))
@app.route('/addinternalresult',methods=['GET','POST'])
def addinternalresult():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('SELECT studentid from addstu')
        data=cursor.fetchall()
        cursor.execute('SELECT COURSEID FROM addsub')
        cdata=cursor.fetchall()
        if request.method=='POST':
            id1=request.form['id']
            course=request.form['course']
            int1=request.form['int1']
            int2=request.form['int2']
            imarks1=request.form['imarks1']
            imarks2=request.form['imarks2']
            section=request.form['section']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into internalresults value(%s,%s,%s,%s,%s,%s,%s)',(id1,course,int1,int2,imarks1,imarks2,section))
            cursor.connection.commit()
            flash(f'added successfilly')
            return redirect(url_for('dash'))
        return render_template('addinternalresult.html',data=data,cdata=cdata)
    else:
        return redirect(url_for('login'))
@app.route('/studentrecord')
def studentrecord():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from addstu')
        students_data=cursor.fetchall()
        print(students_data)
        cursor.close()
        return render_template('studentrecord.html',data=students_data)
    else:
        return redirect(url_for('login'))
@app.route('/updaterecords/<studentido>',methods=['GET','POST'])
def updaterecords(studentido):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select studentid,studentname,section,mobile,Address,Department from addstu where studentid=%s',[studentido])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
           studentid=request.form['studentid']
           studentname=request.form['studentname']
           section=request.form['section']
           mobile=request.form['mobile']
           Address=request.form['Address']
           Department=request.form['Department']
           cursor=mydb.cursor(buffered=True)
           cursor.execute('update addstu set studentid=%s,studentname=%s,section=%s,mobile=%s,Address=%s,Department=%s where studentid=%s',[studentid,studentname,section,mobile,Address,Department,studentido])
           mydb.commit()
           cursor.close()
           flash('Records updated successfully')
           return redirect(url_for('studentrecord'))
        return render_template('update.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/deleterecords/<stdid>')
def deleterecords(stdid):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('delete from addstu where studentid=%s',[stdid])
    mydb.commit()
    cursor.close()
    flash('Records deleted successfully')
    return redirect(url_for('studentrecord'))
@app.route('/subjectrecord')
def subjectrecord():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from addsub')
        data=cursor.fetchall()
        print(data)
        cursor.close()
        return render_template('subjectrecord.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/subupdate/<courseido>',methods=['GET','POST'])
def subupdate(courseido):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select courseid,coursetitle,maxmarks from addsub where courseid=%s',[courseido])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
           courseid=request.form['courseid']
           coursetitle=request.form['coursetitle']
           maxmarks=request.form['mmarks']
           cursor=mydb.cursor(buffered=True)
           cursor.execute('update addsub set courseid=%s,coursetitle=%s,maxmarks=%s where courseid=%s',[courseid,coursetitle,maxmarks,courseido])
           mydb.commit()
           cursor.close()
           flash('Records updated successfully')
           return redirect(url_for('subjectrecord'))
        return render_template('subupdate.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/delete/<courseid>')
def delete(courseid):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('delete from addsub where courseid=%s',[courseid])
    mydb.commit()
    cursor.close()
    flash('Records deleted successfully')
    return redirect(url_for('subjectrecord'))
@app.route('/search',methods=['GET','POST'])
def search():
    if session.get('user'):
        if request.method=='POST':
            search=request.form['search']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select a.courseid,a.studentid,a.semister,a.semmarks,i.Internal1,i.internalmarks1,i.Internal2,i.internalmarks2 from addstu as s inner join semresults as a on s.studentid=a.studentid  inner join internalresults as i on s.studentid=i.studentid and i.courseid=a.courseid where s.studentid=%s',[search])
            data=cursor.fetchall()
            mydb.commit()
            cursor.close()
            return render_template('resultsearch.html',data=data)
     else:
        return render_template('resultsearch.html')
   
@app.route('/editsemresult',methods=['GET','POST'])
def editsemresult():
    if session.get('user'):
        if request.method=='POST':
            search=request.form['search']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select a.courseid,a.studentid,a.semister,a.semmarks,i.Internal1,i.internalmarks1,i.Internal2,i.internalmarks2 from addstu as s inner join semresults as a on s.studentid=a.studentid  inner join internalresults as i on s.studentid=i.studentid and i.courseid=a.courseid')
            data=cursor.fetchall()
            mydb.commit()
            cursor.close()
            return render_template('showsem.html',data=data)
        return render_template('showsem.html')
@app.route('/deletes/<courseid>/<studentid>')
def deletes(courseid,studentid):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('delete from semresults where courseid=%s and studentid=%s',[courseid,studentid])
    cursor.execute('delete from internalresults where courseid=%s and studentid=%s',[courseid,studentid])
    mydb.commit()
    cursor.close()
    flash('Records deleted successfully')
    return redirect(url_for('dash'))
@app.route('/editinternalresult',methods=['GET','POST'])
def editinternalresult():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select i.courseid,i.studentid,i.Internal1,i.internalmarks1,i.Internal2,i.internalmarks2 from addstu as s inner join internalresults as i on s.studentid=i.studentid')
        data=cursor.fetchall()
        if request.method=='POST':
            search=request.form['search']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select a.courseid,a.studentid,a.semister,a.semmarks,i.Internal1,i.internalmarks1,i.Internal2,i.internalmarks2 from addstu as s inner join semresults as a on s.studentid=a.studentid  inner join internalresults as i on s.studentid=i.studentid and i.courseid=a.courseid where s.studentid=%s',[search])
            data=cursor.fetchall()
            mydb.commit()
            cursor.close()
            return render_template('showinternal.html',data=data)
        return render_template('showinternal.html',data=data)
@app.route('/deleted/<courseid>/<studentid>')
def deleted(courseid,studentid):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('delete from internalresults where courseid=%s and studentid=%s',[courseid,studentid])
    mydb.commit()
    cursor.close()
    flash('Records deleted successfully')
    return redirect(url_for('dash'))
if __name__=="__main__":
    app.run(use_reloader=True,debug=True)
    
