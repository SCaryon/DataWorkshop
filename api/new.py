from flask import Blueprint, render_template, session
from model import user


new = Blueprint('new',__name__,template_folder='../templates_new')
@new.route("/new/")
def home():

    session['cluster_method'] = 'KMeans'
    session['embedding_method'] = 'Principal_Component_Analysis'
    session['visualization_method'] = 'Radviz'
    session['cluster_parameters'] = {}
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        print(user1)
        return render_template('front.html', user=user1)
    else:
        return render_template('front.html')


@new.route('/new/logout/')
def logout():
    session.clear()
    return home()

@new.route("/new/login/")
def login():
    return render_template('login.html')

@new.route("/new/signup/")
def signup():
    return render_template('signup.html')

@new.route("/new/term1/")
def term1():
    return render_template('term1.html')

@new.route("/new/term2")
def term2():
    return render_template('term2.html')

@new.route("/new/my/")
def my():
    return render_template('my.html')

@new.route("/new/first")
def world2():
    return "Hello Wo!"