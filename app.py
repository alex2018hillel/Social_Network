from flask import (Flask, g, render_template, flash, redirect, url_for, abort, request, jsonify)
from flask_restful import Api
import logging
from logging.handlers import RotatingFileHandler
import models, resources, forms
from settings import RANDOM_STRING, FLASK_HOST, FLASK_PORT, DEBUG, JWT_SECRET_KEY
from flask_jwt_extended import JWTManager, current_user, get_current_user, set_access_cookies, set_refresh_cookies, \
	unset_jwt_cookies
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity
                                )

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = RANDOM_STRING
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
'''
turn ON, if use the JWT access cookie:
# app.config['JWT_TOKEN_LOCATION'] =  ["cookies"]
and turn OFF: app.config['JWT_TOKEN_LOCATION'] =  ["headers"]
'''
app.config['JWT_TOKEN_LOCATION'] =  ["headers"]


jwt = JWTManager(app)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
	jti = decrypted_token['jti']
	return models.RevokedTokenModel.is_jti_blacklisted(jti)


api.add_resource(resources.UserRegistration, '/api/registration')
api.add_resource(resources.UserLogin, '/api/login')
api.add_resource(resources.PostCreate, '/post/create')
api.add_resource(resources.PostLike, '/api/post/like')
api.add_resource(resources.LikeCount, '/api/analitics/')
api.add_resource(resources.UserActivity, '/api/activity/<user>')

api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')



@app.before_request
def before_request():
	"""Connect to database before each request
		g is a global object, passed around all time in flask, used to setup things which
		we wanna have available everywhere.
	"""
	g.db = models.db
	g.db.connect()
	g.user = current_user

def init_app_logger():
	handler = RotatingFileHandler('logs/blog.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.DEBUG)
	file_formatter = logging.Formatter('[%(asctime)s] p%(process) {%(pathname)s:%(lineno)d}'
									   '%(levelname)s - %(message)s'
									   )
	handler.setFormatter(file_formatter)
	app.logger.addHandler(handler)
	app.logger.setLevel(logging.DEBUG)


@app.after_request
def after_request(response):
	"""close all database connection after each request"""
	g.db.close()
	return response


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream = stream, current_user = g.user)


@app.route('/register', methods = ('GET','POST'))
def register():
	form = forms.RegisterForm()
	if form.validate_on_submit():
		flash("Congrats, Registered Successfully!", "success")
		models.User.create_user(
			username = form.username.data,
			email = form.email.data,
			password = form.password.data
		)
		return redirect(url_for('index'))
	return render_template('register.html', form = form, current_user = g.user)


@app.route('/login', methods = ('GET', 'POST'))
def login():
	if request.method == "GET":
		return render_template('login.html',
							   title = 'Sign In',
							   current_user = g.user)
	elif request.method == "POST":
			username = request.form["username"]
			password = request.form["password"]
			access_token = create_access_token(identity = username)
			refresh_token = create_refresh_token(identity = username)
			resp = jsonify({'login': True})
			set_access_cookies(resp, access_token)
			set_refresh_cookies(resp, refresh_token)
			return redirect(url_for("index", current_user = get_jwt_identity()))


@app.route('/new_post', methods = ('GET', 'POST'))
@jwt_refresh_token_required
def post():
	form = forms.PostForm()
	if form.validate_on_submit():
		models.Post.create(user_id = g.user.id,
							content = form.content.data.strip())
		flash("Message Posted: Thanks!", "success")
		return redirect(url_for('index'))
	return render_template('post.html', form = form, current_user = g.user)


@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route('/post/<int:post_id>')
def view_post(post_id):
	'''
	View selected post
	'''
	posts = models.Post.select().where(models.Post.id == post_id)
	if posts.count() == 0:
		abort(404)
	return render_template('stream.html', stream = posts, current_user = current_user)


@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
	# Create the new access token
	current_user = get_jwt_identity()
	access_token = create_access_token(identity=current_user)

	# Set the JWT access cookie in the response
	resp = jsonify({'refresh': True})
	set_access_cookies(resp, access_token)
	return resp, 200


@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404


if __name__ == '__main__':
	init_app_logger()
	models.initialize()
	app.run(debug=DEBUG,host = FLASK_HOST, port = FLASK_PORT)
