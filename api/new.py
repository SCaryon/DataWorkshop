from flask import Blueprint, render_template, abort


new = Blueprint('new',__name__,template_folder='../templates_new')
@new.route("/new/")
def world():
    return render_template('front.html')



@new.route("/new/first")
def world2():
    return "Hello Wo!"