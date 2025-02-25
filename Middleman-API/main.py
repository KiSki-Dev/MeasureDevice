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


#* Functions
async def getDataFromDB(name, timeUnit):
    conn = sqlite3.connect(dbURL)
    cur = conn.cursor()

    cur.execute("SELECT * FROM " + name + timeUnit)
    rows = cur.fetchall()
    conn.close()
    return json.dumps(rows)

async def refreshData():
    print("-"*11 + str(datetime.now()) + "-"*11)
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
            
        await checkMinAmount(conn, f"{type.name}Min", f"{type.name}Hours")

    for type in types:
        await checkHoursAmount(conn, f"{type.name}Hours", f"{type.name}Days")

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

#! Check if a amount is worthy to be averaged or to be deleted (Min Data)
async def checkMinAmount(conn, tableName, nextTable):
    toDeleteIDs = []
    toAverage = []
    allowAverage = False

    cur = conn.cursor();
    cur.execute(f"SELECT * FROM {tableName}")
    rows = cur.fetchall()
    nowTS = int(datetime.now().timestamp())

    for row in rows:
        timestampAgo = int(nowTS - int(row[1]))

        if (timestampAgo > 7300): # if older then ~2 hours
            toDeleteIDs.append(row[2])

        if (3700 <= timestampAgo <= 7300): # Check if timestamp is not older then ~2 hours
            toAverage.append(row)
            if (7200 <= timestampAgo <= 7300): # If any value is older then ~1,9 hours and younger then ~2,1 hours
                allowAverage = True

    if (allowAverage): 
        await AverageAndSave(conn, nextTable, toAverage, "Min")
        for row in toAverage:
            toDeleteIDs.append(row[2])
    
    await deleteValues(conn, tableName, toDeleteIDs)

#! Check if a amount is worthy to be averaged or to be deleted (Hours Data)
async def checkHoursAmount(conn, tableName, nextTable):
    toDeleteIDs = []
    toAverage = []
    allowAverage = False

    cur = conn.cursor();
    cur.execute(f"SELECT * FROM {tableName}")
    rows = cur.fetchall()
    nowTS = int(datetime.now().timestamp())

    for row in rows:
        timestampAgo = int(nowTS - int(row[1]))

        if (timestampAgo > 178200): # if older then ~2 days
            toDeleteIDs.append(row[2])

        if (88128 <= timestampAgo <= 178200): # Check if timestamp is not older then 49,5 hours
            toAverage.append(row)
            if (172260 <= timestampAgo <= 178200): # If any value is older then 47,5 hours and younger then 49,5 hours
                allowAverage = True

    if (allowAverage): 
        await AverageAndSave(conn, nextTable, toAverage, "Hours")
        for row in toAverage:
            toDeleteIDs.append(row[2])
    
    await deleteValues(conn, tableName, toDeleteIDs)

#! Gets average of a List of values and saves it to the database in the next unit's table
async def AverageAndSave(conn, tableName, averageValues, toReplace):
    if (len(averageValues) > 1): # Check if there are enough values to average
        values = []
        for value in averageValues:
            values.append(value[0])

        average = round(statistics.mean(values), 2)
        print(f"{tableName}s Average is {average}")
        cur = conn.cursor();

        now = datetime.now()
        if (toReplace == "Min"):
            nowRounded = now.replace(minute=0, second=0, microsecond=0)
        elif (toReplace == "Hours"):
            nowRounded = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            nowRounded = now.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
        unix = int(nowRounded.timestamp())

        cur.execute(f''' INSERT INTO {tableName}(value,timestamp)
                VALUES(?,?) ''', (average, unix))
        conn.commit()
        print(f"Added Row to {tableName}. ID: {cur.lastrowid}")
        return True
    return False

#! Deletes a list of values from a table
async def deleteValues(conn, tableName, deleteIDs):
    cur = conn.cursor();
    query = "DELETE FROM " + tableName + " WHERE id IN ({})".format(", ".join("?" * len(deleteIDs)))
    cur.execute(query, deleteIDs)
    print(f"Removed {len(deleteIDs)} Rows from {tableName}. Last row ID: {cur.lastrowid}")
    conn.commit()



@scheduler.scheduled_job(trigger="interval", seconds=60)
async def refreshDataJob():
    status = await refreshData()
    print(str(status))

if __name__ == '__main__':
    uptime = int(datetime.now().timestamp())
    uvicorn.run(app, host="0.0.0.0", port=8000)