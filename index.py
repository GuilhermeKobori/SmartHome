from flask import Flask, render_template, request
import sqlite3 as sql
import datetime

app = Flask(__name__)

@app.route('/index')
def index():
    currentDate = datetime.datetime.now()
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    interval=request.args.get('Interval')
    if interval=="month":
        interval="This month"
        previousMonth = currentDate - datetime.timedelta(days = 30)
        query = 'SELECT * from Values_15min WHERE Date IN ("%s", "%s")' % (currentDate.strftime("%d/%m/%Y"), previousMonth.strftime("%d/%m/%Y"))
        cur.execute("SELECT * FROM Values_day")
        rows = cur.fetchall();
        return render_template('daily.html', rows = rows, interval=interval)
    elif interval=="week":
        interval="This week"
        previousWeek = currentDate - datetime.timedelta(weeks = 1)
        query = 'SELECT * from Values_15min WHERE Date IN ("%s", "%s")' % (currentDate.strftime("%d/%m/%Y"), previousWeek.strftime("%d/%m/%Y"))
        cur.execute("SELECT * FROM Values_Day")
        rows = cur.fetchall();
        return render_template('daily.html', rows = rows, interval=interval)
    else :
        interval="Today"
        #print("select * from Values_15min WHERE Date = " + currentDate.strftime("%d/%m/%Y"))
        query = 'SELECT * from Values_15min WHERE Date = "%s"' % (currentDate.strftime("%d/%m/%Y"))
        cur.execute(query)
        rows = cur.fetchall();
        return render_template('index.html', rows = rows, interval=interval)

@app.route('/interval')
def interval():
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    frequency = request.args.get('frequency')
    #if frequency change table
    query = 'SELECT * from Values_15min WHERE Date IN ("%s", "%s")' % (startDate, endDate)
    cur.execute(query)
    rows = cur.fetchall();
   
    return render_template('daily.html', rows = rows)

@app.route('/status')
def status():
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from test")
   
    rows = cur.fetchall();
    return render_template('status.html', rows = rows)

@app.route('/settings')
def settings():
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from test")
   
    rows = cur.fetchall();
    return render_template('index.html', rows = rows)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
