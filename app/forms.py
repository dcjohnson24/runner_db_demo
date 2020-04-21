from wtforms import Form, StringField


class PredictForm(Form):
    search = StringField('Search by runner name')
