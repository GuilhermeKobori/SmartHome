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
        dateInterval = '"' + currentDate.strftime("%d/%m/%Y") + '"'
        for i in range(30):
            previousDate = currentDate - datetime.timedelta(days = i+1)
            dateInterval += ', "' + previousDate.strftime("%d/%m/%Y") + '"'
        query = 'SELECT * from Values_Day WHERE Date IN (%s)' % (dateInterval)
        print(query)
        cur.execute(query)
        rows = cur.fetchall();
        print(rows)
        return render_template('daily.html', rows = rows, interval=interval)
    elif interval=="week":
        interval="This week"
        dateInterval = '"' + currentDate.strftime("%d/%m/%Y") + '"'
        for i in range(7):
            previousDate = currentDate - datetime.timedelta(days = i+1)
            dateInterval += ', "' + previousDate.strftime("%d/%m/%Y") + '"'
        query = 'SELECT * from Values_Day WHERE Date IN (%s)' % (dateInterval)
        print(query)
        cur.execute(query)
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
    cur.execute("select * from temperature_Humidity_Sensor where id = 1")
    temperatureHumiditySensorStatus = cur.fetchone()
    cur.execute("select * from brightness_Sensor where id = 1")
    brightnessSensorStatus = cur.fetchone()
    
    return render_template('status.html', brightnessSensorStatus = brightnessSensorStatus, temperatureHumiditySensorStatus = temperatureHumiditySensorStatus)

@app.route('/settings', methods = ['POST', 'GET'])
def settings():    
    con = sql.connect("measurementData.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    
    if request.method == 'POST':
        result = request.form
        cur.execute("update humidity_Threshold set value = (?) where id = 1", result["humidity"])
        cur.execute("update brightness_Threshold set value = (?) where id = 1", result["brightness"])
        return render_template('settings.html', humidityThreshold = result["humidity"], brightnessThreshold = result["brightness"], alert = 'True')
    else:
        return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)
