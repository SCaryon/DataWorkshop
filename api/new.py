from flask import Blueprint, render_template, abort


new = Blueprint('new',__name__,template_folder='../templates_new')
@new.route("/new/")
def home():
    return render_template('front.html')

@new.route("/login/")
def login():
    return render_template('login.html')

@new.route("/signup/")
def signup():
    return render_template('signup.html')

@new.route("/term1/")
def term1():
    return render_template('term1.html')

@new.route("/term2")
def term2():
    return render_template('term2.html')


@new.route("/new/first")
def world2():
    return "Hello Wo!"