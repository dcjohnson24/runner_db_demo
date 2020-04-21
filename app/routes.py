import sys
from os.path import dirname, abspath, join

path = dirname(dirname(abspath(__file__)))
sys.path.append(join(path, 'predict'))

from flask import request, render_template, make_response, flash, redirect, url_for
from flask import current_app as app
from flask import Blueprint
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
import pandas as pd

from .models import db, Race
from .forms import PredictForm
from predict import predict_runner

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/predict', methods=['GET', 'POST'])
def predict_race_time():
    search = PredictForm(request.form)
    result = ''
    if request.method == 'POST':
        name = search.data['search']
        df = pd.read_sql(db.session.query(Race).statement, con=db.engine)

        if name:
            result = predict_runner(name, df)
        else:
            flash('Please enter a name')

        if not result:
            flash('No result found')
            return redirect(url_for('main.predict_race_time'))

    return render_template('predict.html',
                           title='Gugs DB',
                           form=search,
                           result=result)
