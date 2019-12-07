from flask import Flask, request, redirect, render_template,session, flash
from flask_sqlalchemy import SQLAlchemy

from hashutils import make_pw_hash,check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz1:password@localhost:8889/blogz1'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key='ui2bjsndkj'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id=db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):        

    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(120),unique=True)
    pw_hash=db.Column(db.String(120))
    blogs=db.relationship('Blog',backref='owner')

    def __init__(self,username,password):
        self.username=username
        self.pw_hash=make_pw_hash(password)

    def __repr__(self):
        return self.username    

@app.before_request
def require_login():
    # Allow all routes except write new, that needs user to login
    allowed_routes=['login','signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')        


@app.route('/signup',methods=['POST','GET'])
def signup():
    error1=''
    error2=''
    error3=''
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        verify=request.form['verify']

        if ' ' in username or len(username)<3 or len(username)>20:
            error1="Thats not a valid user name"
       
        if ' ' in password or len(password)<3 or len(password)>20 :
            error2="Thats not a valid password"
            # error3=''
        else:    
            if ' ' in verify or len(verify)<3 or len(verify)>20 or verify!= password :
                error3="Passwords don't match"    
  
       
        if not (error1 or error2 or error3 ):
            existing_user=User.query.filter_by(username=username).first()
            if not existing_user:
                new_user=User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username']=username
                return redirect('/newpost')
            else:
                return '<h1>User already exists</h1>' 
    # if error in creating, ask to reeder details
    
    return render_template('signup.html',error1=error1,error2=error2,error3=error3)                
    

@app.route('/login',methods=['POST','GET'])
def login():
    error=''
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()

        if user and check_pw_hash(password,user.pw_hash):
            session['username']=username
            
        # direct successflly logged in users to
            return redirect('/newpost')
            
        else:
            if not user:
                error= "Invalid user name"
            elif not check_pw_hash(password,user.pw_hash):
                error="Password incorrect"    
            
              

    return render_template('login.html',error=error)
    

@app.route('/')
def index():
    users=User.query.all()
    return render_template('index.html',users=users)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog1=None
    blogs=None
#printing all blogs for a user when user tab clicked on home page
    user=request.args.get('user')
    # /localhost:5000/blog?user=ksdflksd
    username=User.query.filter_by(username=user).first()
    if username:
        blog1=Blog.query.filter_by(owner=username).all()
        return render_template('blog.html',blog1=blog1,blogs=blogs)

# printing blogs list under All posts
    blogs = Blog.query.all()
    return render_template('blog.html',blogs=blogs)
    

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    error1=''
    error2=''
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        if not blog_title:
            error1='Please fill in the title' 
            
        if  blog_body =="":
            error2='Please fill in the body'
             
        if not error1 and not error2:
            owner=User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title,blog_body,owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')     

    
    return render_template('newpost.html',error1=error1,error2=error2) 


@app.route("/blog_dis", methods=['GET'])
def blog_dis():
    blog_id = request.args.get('id')
    # body = request.args.get('body')
    blog_d=Blog.query.filter_by(id=blog_id).first()
    return render_template('blog_dis.html',blog=blog_d)




if __name__ == '__main__':
    app.run()

