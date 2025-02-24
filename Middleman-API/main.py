from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
import json
import time
import statistics
from datetime import datetime
import uvicorn

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler  # runs tasks in the background

arduinoURL = "http://192.168.178.43:4719" # URL to the Arduino
dbURL = "PATH TO SQLTIE DATABASE"

# Set up the scheduler
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Connection successful"}

@app.get("/refresh")
async def refresh():
    status = await dbInsertData()
    return json.loads(status)

# Minute Data
@app.get("/humidityMin")
async def send_humidityMin():
    data = await getDataFromDB("humidity", "Min")
    return json.loads(data)

@app.get("/temperatureMin")
async def send_temperatureMin():
    data = await getDataFromDB("temperature", "Min")
    return json.loads(data)

@app.get("/heatIndexMin")
async def send_heatIndexMin():
    data = await getDataFromDB("heatIndex", "Min")
    return json.loads(data)

@app.get("/lightMin")
async def send_lightMin():
    data = await getDataFromDB("light", "Min")
    return json.loads(data)

@app.get("/voltageMin")
async def send_voltageMin():
    data = await getDataFromDB("voltage", "Min")
    return json.loads(data)

# Hour Data
@app.get("/humidityHour")
async def send_humidityHour():
    data = await getDataFromDB("humidity", "Hours")
    return json.loads(data)

@app.get("/temperatureHour")
async def send_temperatureHour():
    data = await getDataFromDB("temperature", "Hours")
    return json.loads(data)

@app.get("/heatIndexHour")
async def send_heatIndexHour():
    data = await getDataFromDB("heatIndex", "Hours")
    return json.loads(data)

@app.get("/lightHour")
async def send_lightHour():
    data = await getDataFromDB("light", "Hours")
    return json.loads(data)

@app.get("/voltageHour")
async def send_voltageHour():
    data = await getDataFromDB("voltage", "Hours")
    return json.loads(data)

async def getDataFromDB(name, timeUnit):
    conn = sqlite3.connect(dbURL)
    cur = conn.cursor()

    cur.execute("SELECT * FROM " + name + timeUnit)
    rows = cur.fetchall()
    conn.close()
    return json.dumps(rows)

async def dbInsertData():
    conn = sqlite3.connect(dbURL)
    cur = conn.cursor();

    # conn.execute('''CREATE TABLE IF NOT EXISTS temperatureMin
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS lightMin
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS humidityMin
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS heatIndexMin
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS voltageMin
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')

    # conn.execute('''CREATE TABLE IF NOT EXISTS temperatureHours
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS lightHours
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS humidityHours
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS heatIndexHours
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')
    # conn.execute('''CREATE TABLE IF NOT EXISTS voltageHours
    #                 (value INT, timestamp INT, id INTEGER PRIMARY KEY)''')

    # To-Do make Enums for easierer

    unix = int(datetime.now().timestamp())

    humidity = await getDataFromAPI("humidity")
    if (int(humidity["value"]) < 101):
        cur.execute(''' INSERT INTO humidityMin(value,timestamp)
                VALUES(?,?) ''', (humidity["value"], unix))
    await checkAmount(conn, "humidityMin", "humidityHours")

    temperature = await getDataFromAPI("temperature")
    if (int(temperature["value"]) < 60):
        cur.execute(''' INSERT INTO temperatureMin(value,timestamp)
                VALUES(?,?) ''', (temperature["value"], unix))
    await checkAmount(conn, "temperatureMin", "temperatureHours")

    heatIndex = await getDataFromAPI("heatIndex")
    if (int(heatIndex["value"]) < 60):
        cur.execute(''' INSERT INTO heatIndexMin(value,timestamp)
                VALUES(?,?) ''', (heatIndex["value"], unix))
    await checkAmount(conn, "heatIndexMin", "heatIndexHours")

    light = await getDataFromAPI("light")
    if (int(light["value"]) < 101):
        cur.execute(''' INSERT INTO lightMin(value,timestamp)
                VALUES(?,?) ''', (light["value"], unix))
    await checkAmount(conn, "lightMin", "lightHours")

    voltage = await getDataFromAPI("voltage")
    if (float(voltage["value"]) < 60.00):
        cur.execute(''' INSERT INTO voltageMin(value,timestamp)
                VALUES(?,?) ''', (voltage["value"], unix))
    await checkAmount(conn, "voltageMin", "voltageHours")

    conn.commit()
    print("Added Row. ID: " + str(cur.lastrowid))
    cur.close()
    conn.close()
    return json.dumps({"humidity": humidity["value"], "temperature": temperature["value"], "heatIndex": heatIndex["value"], "light": light["value"], "voltage": voltage["value"]})

async def getDataFromAPI(api):
    resp = requests.get(arduinoURL + '/' + api)
    if (resp.status_code == 200):
        respJSON = json.loads(resp.text)
        return respJSON

async def checkAmount(conn, tableName, nextTable):
    toDeleteIDs = []
    toAverage = []
    allowAverage = False

    cur = conn.cursor();
    cur.execute(f"SELECT * FROM {tableName}")
    rows = cur.fetchall()

    for row in rows:
        # print(str(row))
        timestampAgo = int(int(datetime.now().timestamp()) - int(row[1]))

        if (timestampAgo > 7300): # if older then 2 ~hours
            toDeleteIDs.append(row[2])

        if (3700 <= timestampAgo <= 7300): # Check if timestamp is not older then 2 ~hours
            toAverage.append(row)
            if (7200 <= timestampAgo <= 7300):
                allowAverage = True


    if (allowAverage): 
        await AverageAndSave(conn, nextTable, toAverage)
        for row in toAverage:
            toDeleteIDs.append(row[2])
    
    await deleteValues(conn, tableName, toDeleteIDs)

async def AverageAndSave(conn, tableName, averageValues):
    if (len(averageValues) > 1):
        values = []
        for value in averageValues:
            values.append(value[0])

        average = round(statistics.mean(values), 2)
        print(f"{tableName}s Average is {average}")
        cur = conn.cursor();

        now = datetime.now()
        nowRounded = now.replace(minute=0, second=0, microsecond=0)
        unix = int(nowRounded.timestamp())

        cur.execute(f''' INSERT INTO {tableName}(value,timestamp)
                VALUES(?,?) ''', (average, unix))
        conn.commit()
        print(f"Added Row to {tableName}. ID: {cur.lastrowid}")
        return True
    return False

async def deleteValues(conn, tableName, deleteIDs):
    cur = conn.cursor();
    query = "DELETE FROM " + tableName + " WHERE id IN ({})".format(", ".join("?" * len(deleteIDs)))
    cur.execute(query, deleteIDs)
    print(f"Removed {len(deleteIDs)} Rows from {tableName}. Last row ID: {cur.lastrowid}")
    conn.commit()


@scheduler.scheduled_job(trigger="interval", seconds=60)
async def refreshData():
    status = await dbInsertData()
    print(str(status))


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)