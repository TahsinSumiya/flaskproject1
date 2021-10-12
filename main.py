from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from logging import FileHandler,WARNING
from werkzeug.utils import secure_filename
import json
import os
import math
from datetime import date, datetime
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
#json call
local_sever=True
with open('config.json','r')as c:
    params = json.load(c)["params"]

app = Flask(__name__)
#secret key sesison.....................................................
app.secret_key = 'super-secret-key'
#.............................................................................
#mailsection

app.config['Uploader_folder'] = params['upload_location']
app.config.update(

   MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']

)
mail = Mail(app)
#sqlalchemy
if(local_sever):
 app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
 app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

#contact section database connection
class Contacts(db.Model):
    
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
#post section database connection
class Posts(db.Model):
    
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(21), nullable=True)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(21), nullable=False)
    
#index.html
@app.route("/")
def home():
    posts= Posts.query.filter_by().all()
    # [0:params['no-of-posts']]
    last = math.ceil(len(posts)/int(params['no-of-posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
       page = 1
    page= int(page)
    posts = posts[(page-1)*int(params['no-of-posts']): (page-1)*int(params['no-of-posts'])+ int(params['no-of-posts'])]
    if (page==1):
        prev = "#"
        next ="/?page="+ str(page+1)
    elif (page == last):
        
        prev ="/?page="+ str(page-1)
        next = "#"
    else:
        prev ="/?page="+ str(page-1)
        next ="/?page="+ str(page+1)



    return render_template('index.html',params=params, posts=posts,prev=prev,next=next)
#post section
@app.route("/post/<string:post_slug>",methods = ['GET'])
def post_route(post_slug):
 post = Posts.query.filter_by(slug=post_slug).first()
     

 return render_template('post.html',params=params, post=post)
#about
@app.route("/about")
def about():
    return render_template('about.html',params=params)

#dashboard.......................................................................................
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    if ('user' in session and session['user'] == params['admin_user']):
       posts = Posts.query.all()
       return render_template('dashboard.html', params=params, posts=posts)


    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_pass']):
            #set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params , posts=posts)

    return render_template('login.html', params=params)



@app.route("/edit/<string:sno>",methods = ['GET','POST'])
def edit(sno):
 if ('user' in session and session['user'] == params['admin_user']):
     if request.method == 'POST':
         t_title = request.form.get('title')
         t_tagline = request.form.get('tagline')
         t_slug = request.form.get('slug')
         t_content = request.form.get('content')
         t_img = request.form.get('image')
         date = datetime.now()
         if sno== '0':
             post = Posts(title=t_title,tagline=t_tagline,slug=t_slug,content=t_content,img_file=t_img,date=date)
             db.session.add(post)
             db.session.commit()
         else:
             post = Posts.query.filter_by(sno=sno).first()
             post.title = t_title
             post.tagline= t_tagline
             post.slug= t_slug       #post.param comi ng from the database
             post.content=t_content
             post.img_file=t_img
             post.date=date
             db.session.commit()
             return redirect('/edit/'+sno)
     post = Posts.query.filter_by(sno=sno).first()
     return render_template('edit.html',params=params,post=post,sno=sno)

#uploader......................................................................
@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
     if ('user' in session and session['user'] == params['admin_user']):
         if(request.method=='POST'):
           f=request.files['file1']
           f.save(os.path.join(app.config['Uploader_folder'],secure_filename(f.filename) ))

           return "Uploaded sucessfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')
    



#cointact section........................................................................
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
       
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, email = email, phone_num = phone, mes = message, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New mwssage from ' + name,
         sender=email,
         recipients= [params['gmail-user']],
         body = message + "\n" + phone
         )
    return render_template('contact.html',params=params)

if __name__ == "__main__":
  app.run(debug=True)







