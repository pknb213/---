import flask_login
from flask_login import login_required, current_user, login_user, logout_user
from flask import render_template, request, jsonify
from Flask.py.utils import *
from datetime import timedelta

login_manager = flask_login.LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = u"Session timed out, please re-login"
login_manager.needs_refresh_message_category = "info"


class User:
    # ==========================================================================
    def __init__(self, user_id, email=None, passwd_hash=None,
                 authenticated=False):
        self.user_id = user_id
        self.email = email
        self.passwd_hash = passwd_hash
        self.authenticated = authenticated

    # ==========================================================================
    def __repr__(self):
        r = {
            'user_id': self.user_id,
            'email': self.email,
            'passwd_hash': self.passwd_hash,
            'authenticated': self.authenticated,
        }
        return str(r)

    # ==========================================================================
    def can_login(self, passwd_hash):
        return self.passwd_hash == passwd_hash

    # ==========================================================================
    def is_active(self):
        return True

    # ==========================================================================
    def get_id(self):
        return self.user_id

    # ==========================================================================
    def is_authenticated(self):
        return self.authenticated

    # ==========================================================================
    def is_anonymous(self):
        return False


USERS = {
    "user01": User("user01", passwd_hash='user'),
    "user02": User("user02", passwd_hash='user'),
    "user03": User("user03", passwd_hash='user'),
}


@app.route('/user/<username>')
def showUserProfile(username):
    app.logger.debug('RETRIEVE DATA - USER ID : %s' % username)
    app.logger.debug('RETRIEVE DATA - Check Compelete')
    app.logger.warn('RETRIEVE DATA - Warning... User Not Found.')
    app.logger.error('RETRIEVE DATA - ERR! User unauthenification.')
    return 'USER : %s' % username


@app.before_first_request
def before_request():
    #session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


# 사용자 DB로 바꿔야함
@login_manager.user_loader
def user_loader(user_id):
    return USERS[user_id]


@app.route("/api/auth_func", methods=['POST'])
@login_required
def auth_func():
    user = current_user
    json_res = {'ok': True, 'msg': 'auth_func(%s),user_id=%s'
                                   % (request.json, user.user_id)}
    return jsonify(json_res)


@app.route("/api/notauth_func", methods=['POST'])
def notauth_func():
    json_res = {'ok': True, 'msg': 'notauth_func(%s)'
                                   % request.json}
    return jsonify(json_res)


@app.route('/api/login', methods=['POST'])
def login():
    # user_id = request.json['user_id']
    # passwd_hash = request.json['passwd_hash']
    user_id = request.values.get('user_id')
    passwd_hash = request.values.get('passwd_hash')
    if user_id not in USERS:
        json_res = {'ok': False, 'error': 'Invalid user_id or password'}
    elif not USERS[user_id].can_login(passwd_hash):
        json_res = {'ok': False, 'error': 'Invalid user_id or password'}
    else:
        json_res = {'ok': True, 'msg': 'user <%s> logined' % user_id}
        USERS[user_id].authenticated = True
        login_user(USERS[user_id], remember=True)  # remember is cookie

    if not json_res['ok']:
        #return jsonify(json_res)
        return render_template('error.html', title='Login Fail :(', str='Please... retry the login.', url='main_login')
    else:
        return render_template('menu.html')


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    json_res = {'ok': True, 'msg': 'user <%s> logout' % user.user_id}
    logout_user()
    return jsonify(json_res)


