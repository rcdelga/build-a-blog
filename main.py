from flask import Flask, request, redirect, render_template, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = "build-a-blog"

class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.Text)
	deleted = db.Column(db.Boolean)
	post_date = db.Column(db.DateTime)

	def __init__(self,title,body,post_date=None):
		self.title = title
		self.body = body
		if post_date is None:
			post_date = datetime.now()
		self.post_date = post_date
		self.deleted = False

	def __repr__(self):
		# return '<Post %r>' % self.title
		return "<Blog(id='%r', title='%r', body='%r', post_date=%r, deleted='%r')>" % (self.id, self.title, self.body, self.post_date, self.deleted)



def all_active_blogs():
	return Blog.query.order_by(Blog.post_date.desc()).all()

def get_blog_post(id):
	return Blog.query.get(id)

def valid_title(data):
	if 0 < len(data) < 121:
		return True
	else:
		return False

def valid_body(data):
	if 0 < len(data):
		return True
	else:
		return False



@app.route("/")
def index():
	return redirect('/blog')

@app.route("/blog")
def blogs():
	count = int(request.cookies.get('visit-count', 0))
	count += 1
	message = "You have visited this page {0} time(s).".format(str(count))

	# resp = make_response(message)
	# resp.set_cookie('visit-count', str(count))
	# return resp

	bid = request.args.get('id')

	if bid:
		return render_template('id.html',post=get_blog_post(bid))
	else:
		resp = make_response(render_template('blog.html',blogs=all_active_blogs(),message=message))
		resp.set_cookie('visit-count', str(count))
		return resp


@app.route("/newpost")
def new_post():
	return render_template('newpost.html')

@app.route("/add_blog", methods=['POST'])
def add_post():
	new_title = request.form['new_blog_title']
	new_body = request.form['new_blog_body']

	new_title_error = ''
	new_body_error = ''

	blank_error = "Blank Entry: Please fill out empty field."

	if not valid_title(new_title):
		new_title_error = blank_error
	if not valid_body(new_body):
		new_body_error = blank_error
	if not new_title_error and not new_body_error:
		new_blog = Blog(new_title,new_body)
		db.session.add(new_blog)
		db.session.commit()
		new_id = Blog.query.filter_by(title=new_title,body=new_body).first().id
		return redirect("/blog?id={0}".format(new_id))
	else:
		return render_template("newpost.html",new_blog_title=new_title,new_title_error=new_title_error,new_blog_body=new_body,new_body_error=new_body_error)

if __name__ == "__main__":
	app.run()