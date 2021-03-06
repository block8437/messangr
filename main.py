from flask import *
from werkzeug import secure_filename
import lib, data, os, uuid, whirlpool

DATA = data.MessangrPostsData()

app = Flask(__name__)

def generateUserID(ip):
	s = ip + " " + str(uuid.uuid4())
	return whirlpool.new(s).hexdigest()[:10]


@app.route('/rpost/<post>', methods=['POST'])
def post_reply(post):
	if not 'uid' in session:
		session['uid'] = generateUserID(request.remote_addr)
	if post == "":
		return "Error, post unidentified<br><a href='" + url_for("index") + "'>Home</a>"
	if DATA.getPostID(post) == None:
		return "Error, post unidentified<br><a href='" + url_for("index") + "'>Home</a>"

	message = request.form['message']
	if len(message) < 2:
		return "Post unsuccessfull!<br><a href='" + url_for('reply', post=post) + "'>Back to post</a>" 
	id = escape(session['uid'])

	try:
		f = request.files['file']
		fn = secure_filename(f.filename)
		if fn.strip() == "":
			fn == ""
		else:
			ext = fn.split('.')[-1]
			allowed_ext = ["jpg","jpeg","png", "bmp"]
			if not ext in allowed_ext:
				return "Invalid File Format, only accepts '" + ' '.join(allowed_ext)  + "' received '" + ext + "'"

			f.save('static/uploads/' + fn)
	except:
		fn = ""

	p = DATA.addComment(id, fn, message, post)

	if p:
		return "Post successfull!<br><a href='" + url_for('reply', post=post) + "'>Back to post</a>"
	else:
		return "Post unsuccessfull!<br><a href='" + url_for('reply', post=post) + "'>Back to post</a>" 

@app.route('/r/<post>')
def reply(post):
	if not 'uid' in session:
		session['uid'] = generateUserID(request.remote_addr)
	comments = DATA.getPostComments(post)
	post = DATA.getPostID(post)
	if post == None:
		return "Post not found<br><a href='" + url_for("index") + "'>Home</a>"
	return render_template("posts.html", post=post, comments=comments)

@app.route('/post',methods=['POST'])
def post():
	if not 'uid' in session:
		session['uid'] = generateUserID(request.remote_addr)

	id = escape(session['uid'])
	message = request.form['message']

	f = request.files['file']
	fn = secure_filename(f.filename)
	ext = fn.split('.')[-1]
	allowed_ext = ["jpg","jpeg","png"]
	if not ext in allowed_ext:
		return "Invalid File Format, only accepts '" + ' '.join(allowed_ext)  + "' received '" + ext + "'"

	f.save('static/uploads/' + fn)

	p = DATA.addPost(id, fn, message)

	if p:
		return "Post successfull!<br><a href='" + url_for('index') + "'>Home</a>"
	else:
		return "Post unsuccessfull!<br><a href='" + url_for('index') + "'>Home</a>" 

@app.route('/p/<page>')
def pageN(page):
	if page == "":
		page = 0
	else:
		try:
			page = int(page)
		except:
			page = 0

	if not 'uid' in session:
		session['uid'] = generateUserID(request.remote_addr)

	global DATA

	posts = DATA.getPosts(page=page,amount=10)
	comments = {}

	for post in posts:
		comments[post[3]] = DATA.getPostComments(post[4])[:2]
	
	return render_template("index.html", posts=posts, comments=comments)

@app.route('/')
def index():
	if not 'uid' in session:
		session['uid'] = generateUserID(request.remote_addr)

	global DATA
	
	posts = DATA.getPosts(page=0)
	comments = {}

	for post in posts:
		comments[post[3]] = DATA.getPostComments(post[4])[:2]
	
	return render_template("index.html", posts=posts, comments=comments)

if __name__ == "__main__":
	app.secret_key = os.urandom(24)

	dev = False
	if debug:
		app.run(host="127.0.0.1",port=8080, debug=True)
	else:
		app.run(host="0.0.0.0", port=80, debug=False)