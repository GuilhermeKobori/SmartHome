from flask import Flask, render_template, request
import sqlite3 as sql
from datetime import datetime

app = Flask(__name__)

@app.route('/')
@app.route('/Current')
def index():
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    interval=request.args.get('Interval')
    if interval=="month":
        interval="This month"
        cur.execute("SELECT * FROM test")
    elif interval=="week":
        interval="This week"
        cur.execute("SELECT * FROM test")
    else :
        interval="Today"
        cur.execute("select * from test")
    rows = cur.fetchall();
    return render_template('index.html', rows = rows, interval=interval)

@app.route('/Archive')
def archive():
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
   
    cur = con.cursor()
    
   
    rows = cur.fetchall();
    return render_template('index.html', rows = rows)

@app.route('/Status')
def status():
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from test")
   
    rows = cur.fetchall();
    return render_template('index.html', rows = rows)

@app.route('/Settings')
def settings():
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from test")
   
    rows = cur.fetchall();
    return render_template('index.html', rows = rows)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')