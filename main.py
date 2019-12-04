from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:bui123BUI@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title,body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def blog():

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
            new_blog = Blog(blog_title,blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')     

    
    return render_template('newpost.html',error1=error1,error2=error2) 


@app.route("/blog_dis", methods=['GET'])
def blog_dis():
    blog_id = request.args.get('id')
    # body = request.args.get('body')
    blog_d=Blog.query.filter_by(id=blog_id).first()
    return render_template('blog_dis.html',title=blog_d.title,body=blog_d.body)

if __name__ == '__main__':
    app.run()

