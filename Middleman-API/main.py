from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
import json
import statistics
from datetime import datetime
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from enum import Enum

arduinoURL = "http://???.???.???.???:4719" # URL to the Arduino
dbURL = "" # Path to SQLite Database
uptime = 0

class types(Enum):
    humidity = 1
    temperature = 2
    heatIndex = 3
    light = 4
    voltage = 5

class units(Enum):
    Min = 1
    Hours = 2
    Days = 3

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

# All API Routes
@app.get("/")
async def root():
    return {"uptime": uptime - int(datetime.now().timestamp())}

@app.get("/force-refresh")
async def forceRefreshData():
    status = await refreshData()
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

# Day Data
@app.get("/humidityDay")
async def send_humidityHour():
    data = await getDataFromDB("humidity", "Days")
    return json.loads(data)

@app.get("/temperatureDay")
async def send_temperatureHour():
    data = await getDataFromDB("temperature", "Days")
    return json.loads(data)

@app.get("/heatIndexDay")
async def send_heatIndexHour():
    data = await getDataFromDB("heatIndex", "Days")
    return json.loads(data)

@app.get("/lightDay")
async def send_lightHour():
    data = await getDataFromDB("light", "Days")
    return json.loads(data)

@app.get("/voltageDay")
async def send_voltageHour():
    data = await getDataFromDB("voltage", "Days")
    return json.loads(data)


# Functions
async def getDataFromDB(name, timeUnit):
    conn = sqlite3.connect(dbURL)
    cur = conn.cursor()

    cur.execute("SELECT * FROM " + name + timeUnit)
    rows = cur.fetchall()
    conn.close()
    return json.dumps(rows)

async def refreshData():
    conn = sqlite3.connect(dbURL)
    cur = conn.cursor();

    status = {}

    unix = int(datetime.now().timestamp())

    for type in types:
        apiData = await getDataFromArduino(type.name)
        status[type.name] = float(apiData["value"])
        if (float(apiData["value"]) < 101): # Check if value is not wrong (e.g. 1000%)
            cur.execute(f''' INSERT INTO {type.name}Min(value,timestamp)
                VALUES(?,?) ''', (apiData["value"], unix))
        await checkAmount(conn, f"{type.name}", "Min")

    for type in types:
        await checkAmount(conn, f"{type.name}", "Hours")

    conn.commit()
    print("Added Row. ID: " + str(cur.lastrowid))
    cur.close()
    conn.close()
    return json.dumps(status)

async def getDataFromArduino(api):
    resp = requests.get(arduinoURL + '/' + api)
    if (resp.status_code == 200):
        respJSON = json.loads(resp.text)
        return respJSON
    else:
        return {"value": 100000}

# Check if a amount is worthy to be averaged or to be deleted of the unit
async def checkAmount(conn, tableName, unit):
    cur = conn.cursor();
    cur.execute(f"SELECT * FROM {tableName}{unit}")
    rows = cur.fetchall()

    currentTimestamp = int(datetime.now().timestamp())
    toDeleteIDs = []
    toAverage = []
    allowAverage = False

    if (unit == "Min"):
        maxTime = 7300 # ~2 hours
        minTime = 3700 # ~1 hour
        betweenTime = 7150 # ~2 hours - 10 minutes
    elif (unit == "Hours"):
        maxTime = 173800 # ~2 days
        minTime = 87400 # ~1 day
        betweenTime = 164160 # ~1,8 days

    for row in rows:
        timestampAgo = int(currentTimestamp - row[1])

        if (timestampAgo > maxTime):
            toDeleteIDs.append(row[2])

        if (minTime <= timestampAgo <= maxTime): # Check if timestamp is not older then max Time
            toAverage.append(row)
            if (betweenTime <= timestampAgo <= maxTime):
                allowAverage = True

    if (allowAverage): 
        await AverageAndSave(conn, tableName, units(units[unit].value + 1).name, toAverage)
        for row in toAverage:
            toDeleteIDs.append(row[2])
    
    await deleteValues(conn, tableName, unit, toDeleteIDs)

# Gets average of a List of values and saves it to the database in the next unit's table
async def AverageAndSave(conn, tableName, unit, averageValues): # Unit = next unit (e.g. previous Min -> Hours)
    if (len(averageValues) > 1):
        values = []
        for value in averageValues:
            values.append(value[0])

        average = round(statistics.mean(values), 2)
        cur = conn.cursor();

        now = datetime.now()
        if (unit == "Hours"):
            nowRounded = now.replace(minute=0, second=0, microsecond=0)
        elif (unit == "Days"):
            nowRounded = now.replace(hour=0, minute=0, second=0, microsecond=0)
        unix = int(nowRounded.timestamp())

        cur.execute(f''' INSERT INTO {tableName}{unit}(value,timestamp)
                VALUES(?,?) ''', (average, unix))
        conn.commit()
        print(f"{tableName}{unit}'s Average is {average}. Row ID: {cur.lastrowid}")
        return True
    return False

# Deletes old and unused values from the database table
async def deleteValues(conn, tableName, unit, deleteIDs):
    cur = conn.cursor();
    query = "DELETE FROM " + tableName + unit + " WHERE id IN ({})".format(", ".join("?" * len(deleteIDs)))
    cur.execute(query, deleteIDs)
    print(f"Removed {len(deleteIDs)} Rows from {tableName}{unit}. Last row ID: {cur.lastrowid}")
    conn.commit()


@scheduler.scheduled_job(trigger="interval", seconds=60)
async def refreshDataJob():
    status = await refreshData()
    print(str(status))


if __name__ == '__main__':
    uptime = int(datetime.now().timestamp())
    uvicorn.run(app, host="0.0.0.0", port=8000)