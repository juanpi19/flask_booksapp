from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import sqlite3
import smtplib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    own = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(70), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.id




@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/facts')
def facts():
    return render_template('facts.html')

@app.route('/list', methods=['POST', 'GET'])
def list():
    x = 0
    yes = ''
    no = ''
    conn = sqlite3.connect('books.db')
    df = pd.read_sql_query('SELECT * FROM Books', conn)
    if request.method == 'POST':
        x = request.form['name']

    for i in df.name:
        if i == x:
            yes = df[df.name == x].reset_index()
            break

    if i != x:
        no = 'Book not found'

    x = 0
    for i in df.own:
        if i == 'yes':
            x += 1
        elif i == 'Yes':
            x += 1
        else:
            pass

    message = 'Your book has been added to your list'
    if request.method == 'POST':
        record = Books(name = request.form['name'], author = request.form['author'], own = request.form['own'], description = request.form['description'])


        try:
            db.session.add(record)
            db.session.commit()
            return redirect('/list')
        except:
            return "There was an error adding your record"

    else:
        p = Books.query.order_by(Books.author)
        return render_template('list.html', p=p, message=message, x=x, yes=yes, no=no)


@app.route('/search', methods=['POST', 'GET'])
def search():
    conn = sqlite3.connect('books.db')
    df = pd.read_sql_query('SELECT * FROM Books', conn)
    descrip = request.form['name2']

    l = df[df.name == descrip].description


    return render_template('list.html', descrip=descrip, l=l)


@app.route('/recommendation', methods=['POST', 'GET'])
def recommendation():
    r_email = request.form.get('r_email')
    r_recommendation = request.form.get('r_recommendation')
    r_email2 = 'projects.creativity.growth@gmail.com'

    message = "We have received your recommendation. It will be taken into consideration shortly..."
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("projects.creativity.growth@gmail.com", 'juanpablo14')
    server.sendmail("projects.creativity.growth@gmail.com", r_email, message)
    server.sendmail('projects.creativity.growth@gmail.com', r_email2, r_recommendation)

    return render_template('facts.html')


@app.route('/delete/<string:name>', methods=['POST', 'GET'])
def delete(name):
    record_to_delete = Books.query.get_or_404(name)

    try:
        db.session.delete(record_to_delete)
        db.session.commit()
        return redirect('/list')
    except:
        return "The record could not be deleted"
