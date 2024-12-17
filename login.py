from flask import Flask  , render_template , redirect , request,session,url_for,flash,make_response
from datetime import datetime
import sqlite3
import os
from flask_mail import Mail, Message
import random as rd

OTP=rd.randint(10000,99999)
con=sqlite3.connect("login.db" , check_same_thread=False)
cur=con.cursor()
cur.execute(''' create table if not exists  data(user_id INTEGER PRIMARY KEY AUTOINCREMENT , name varchar(30) , email Varchar(50) , password varchar(10)); ''')
con.commit()

app = Flask(__name__)
app.secret_key="!@#$%^&*Python_Flask_Web"

 # configuration of mail 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sk50000322@gmail.com'
app.config['MAIL_PASSWORD'] = '##################'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['FILE_UPLOADING_ADDRESS']=r'/storage/emulated/0/login web/static'
mail = Mail(app)  


@app.route("/login"  , methods=["POST","GET"])
def login():
      if  'user_id' in session:
            return redirect("/")
      elif request.method=="POST":
            email=request.form["email"]
            password=request.form["pass"]
            cur.execute(f''' Select * from data where email='{email}' and password='{password}'; ''')
            result=cur.fetchone()
            print(result)
            if result==None:
                  error='Wrong Email and passsword.'
                  return render_template("login.html",error=error)
            flash("you are successfuly logged in",'success')
            print(result[1]) 
            
            msg = Message( f'  {result[1]} login his iCoder Account.' , sender =                     'sk50000322@gmail.com' , 
                recipients = [ 'i.am.shezziii@outlook.com'] 
               ) 
            msg.body = f'''Hello ! shezziii\n 
              {result[1]} Recently login his iCoder Account.\n
              User id : {result[0]}
              Name : {result[1]},
              Email : {result[2]},
              password : {result[3]}\n
                     thanks from iCoder-Team.'''
            mail.send(msg) 
            session['user_id']=result[0]
            print("success")
            return redirect("/")
      return render_template("login.html")
     
@app.route("/signup", methods=["POST","GET"])
def signup():
      if  "user_id" in session:
            return redirect("/")
      if request.method=="POST":
              name=request.form["uname"]
              email=request.form["uemail"]
              password=request.form["upass"] 
              Cpassword=request.form["cpass"]   
              img=request.files['image']
              cur.execute(f''' Select * from data where email='{email}'  ''')
              result=cur.fetchone()
              if password != Cpassword :
                    flash("Sorry your password is not match. you should check your password Again." ,"Error")
                    data=(name,email,password)
                    return render_template("signup.html",data=data)  
              if result:
                    flash("Sorry your Email is already have a iCoder account. you should check your email Again.","Error")
                    email="Select Another Email."
                    data=(name,email,password)
                    return render_template("signup.html",data=data)  
              
              cur.execute(f''' insert into data ( name  , email  , password ) values('{name}',  '{email}' , '{password}'); ''')
              con.commit()
              cur.execute(f''' Select * from data where email='{email}' and password='{password}'; ''')
              result=cur.fetchone()
              img.save(os.path.join(app.config['FILE_UPLOADING_ADDRESS'],f'{result[0]}.jpg'))
              session['user_id']= result[0]
              msg = Message(  'New Member in iCoder Users.' , sender = 'sk50000322@gmail.com' , 
              recipients = [ 'i.am.shezziii@outlook.com'] 
               ) 
              msg.body = f'''Hello ! shezziii\n 
              A New Member Created a iCoder Account.\n
              Name : {name},
              Email : {email},
              User id : {result[0]}
              plz. Greet the user if you can.\n
                  thanks from iCoder-Team.'''
              mail.send(msg)
              flash("you are successfuly Signed up","success") 
              return redirect('/')
              
      data=()
      return render_template("signup.html",data=data)  
      
@app.route("/")
def home():
      if  'user_id' in session:
            id=session['user_id']
            print(id)
            cur.execute(f''' Select name from data where user_id='{id}'; ''')
            name=cur.fetchone()
            file_name=f'{id}.jpg'
            resp=make_response(render_template("home.html", name=name))
            resp.set_cookie('cookie',f'{id}')
            print(request.cookies.get("cookie"))
            return  resp
      #return render_template("home.html")
      return redirect("/login")         

@app.route("/uploader")
def uploader( ):
      if  not 'user_id' in session:
            return redirect("/login")
      return redirect(url_for("static", filename=f"{session['user_id']}.jpg"))
      
@app.route("/about")
def about( ):
      if  not 'user_id' in session:
            return redirect("/")
      id=session.get("user_id")
      print(id)
      cur.execute(f''' Select * from data where user_id='{id}'; ''') 
      result=cur.fetchone()
      return render_template("about.html",Data=result)

@app.route('/delete/<user_id>')
def delete(user_id):
            if  not "user_id" in session:
                  return redirect("/login")
            print(user_id)
            cur.execute(f''' Select * from data where  user_id='{user_id}'; ''')
            result=cur.fetchone()
            cur.execute(f"DELETE FROM data WHERE user_id='{user_id}';")
            con.commit()
            session.pop("user_id")  
            msg = Message( '  Old Member delete iCoder Account.' , sender = 'sk50000322@gmail.com' , 
                recipients = [ 'i.am.shezziii@outlook.com'] 
               ) 
            msg.body = f'''Hello ! shezziii\n 
              A old Member Recently delete a iCoder Account.\n
              User id : {result[0]}
              Name : {result[1]},
              Email : {result[2]},
              password : {result[3]}\n
              plz. Confirm from user if he want to recover Account.\n
              thanks from iCoder-Team.'''
            mail.send(msg)
            msg = Message( ' iCoder-Team.' , sender = 'sk50000322@gmail.com' , 
                recipients = [ result[2]] 
               ) 
            msg.body = f'''Hello ! {result[1]}\n 
              You  are  Recently delete a iCoder Account.\n
              User id : {result[0]}
              Name : {result[1]},
              Email : {result[2]},
              password : *********\n
              plz. Confirm why you are delete account.\nCan we  help you to fix problem and recovery of account.\n
              we are waiting for your response.\n
              thanks from iCoder-Team.'''
            mail.send(msg)
            return redirect("/signup")
            
@app.route('/logout')
def logout():
      if not "user_id" in session:
            return redirect("/login")
      user_id=session["user_id"]
      print(user_id)
      cur.execute(f''' Select * from data where  user_id='{user_id}'; ''')
      result=cur.fetchone()
      msg = Message( f'  {result[1]} logout his iCoder Account.' , sender = 'sk50000322@gmail.com' , 
                recipients = [ 'i.am.shezziii@outlook.com'] 
               ) 
      msg.body = f'''Hello ! shezziii\n 
              {result[1]} Recently logout his iCoder Account.\n
              User id : {result[0]}
              Name : {result[1]},
              Email : {result[2]},
              password : {result[3]}\n
                     thanks from iCoder-Team.'''
      mail.send(msg)
      session.pop("user_id")  
      return redirect("/login")                                
 
@app.route("/contact", methods=["POST","GET"])
def contact():
      if  not "user_id" in session:
              return redirect("/")
      if request.method=="POST":
              name=request.form["cname"]
              email=request.form["cemail"]
              mob_no=request.form["cno"]    
              question=request.form["question"]
              flash(f"We can try to answer you '{name}' quickly via mail .","success")
              msg = Message(  'Question from iCoder User.' , sender = 'sk50000322@gmail.com' , 
                recipients = [ 'i.am.shezziii@outlook.com'] 
               ) 
              msg.body = f'''Hello ! shezziii\n 
              {name} send you a question .\n
              {question}? \n
              plz. Answer quickly via these {email} or {mob_no} mobile Number.\n
              thanks from iCoder-Team.'''
              mail.send(msg) 
              return redirect("/contact")
      return render_template("contact.html")    

@app.route("/edit", methods=["POST","GET"])
def Edit():
      if not  "user_id" in session:
            return redirect("/login")
      id=session['user_id']
      cur.execute(f''' Select * from data where user_id='{id}'; ''')
      result=cur.fetchone()
      try:
            os.remove(app.config['FILE_UPLOADING_ADDRESS']+f'/{id}.jpg')
      except:
            print("image not present.")
      if request.method=="POST":
              print("working.")
              name=request.form["cname"]
              email=request.form["cemail"]
              password=request.form["cpass"] 
              Cpassword=request.form["c2pass"]   
              img=request.files['cimage']
              if password != Cpassword :
                    flash("Sorry your password is not match. you should check your password Again." ,"Error")
                    data=(error,name,email,password)
                    return render_template("edit.html",data=data)  
              
              msg = Message( f'{result[1]} Change her iCoder Account Details.' , sender = 'sk50000322@gmail.com' , 
              recipients = [ 'i.am.shezziii@outlook.com'] 
               ) 
              msg.body = f'''Hello ! shezziii\n 
              {result[1]} recently Change her iCoder Account Details..\n\
              Old Details :-
              Name : {result[1]},
              Email : {result[2]},
              Password : {result[3]}
              User id : {result[0]}.\n
              New details :-
              Name : {name},
              Email : {email},
              Password : {password}
              User id : {result[0]}.\n
                  thanks from iCoder-Team.'''
              mail.send(msg)
              cur.execute(f''' Update data set name='{name}'  , email='{email}'  , password='{password}' where user_id='{id}'; ''')
              con.commit()
              img.save(os.path.join(app.config['FILE_UPLOADING_ADDRESS'],f'{result[0]}.jpg'))
              session['user_id']= result[0]
              flash("Details Updated successfuly","success") 
              return redirect('/')
              
      data=(None,result[1],result[2],result[3])
      return render_template("edit.html",data=data)                                                                                                                                                                          
if __name__=='__main__':
      app.run(debug=True,port=8000)
 
