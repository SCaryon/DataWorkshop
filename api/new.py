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



@new.route("/new/first")
def world2():
    return "Hello Wo!"