> [!IMPORTANT]
> **Unfinished** -> Please note that this repository is not finished yet. Please wait until finished before usage.

# "MeasureDevice" using Arduino, API, Database and Webpage
## This is a small Project, I made during my two-week long student Internship at [Janitza](https://www.janitza.com/).
----

![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)


1. An Arduino attachted with multiple sensors reads multiple values like light, temperature and more. 
2. A FastAPI queries the Arduino every mintue for these values. 
3. The FastAPI saves them in a SQLite Database and checks the entire database for old values, which then get averaged and saved in a new table to decrease the Database Size. 
4. A webpage queries the FastAPI for the Values saved in the Database and shows them nice in Charts. 
5. The webpage also allows you to adjust settings from the Arduino.

#### If you dont understand this explanation, this Plan might help you understand:
![alt text](./CommunicationPlan.svg "Communication Plan Diagram")

----

| | Category      | Jump to Category |
|:--------- | ------------- |:-------------:|
|![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white) | Arduino | [:one:](#arduino) |
|![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white) | Database | [:two:](#database) |
| ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) | Middleman-API | [:three:](#middleman-api) |
| ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white) | Webpage | [:four:](#webpage) |
| | Settings | [:five:](#settings) |

<br>**Please note:** While creating the Project, I did not intend to make it very secrue. If you plan on making it publicly avaible or have the used ports open, please modify each code to make it secrue!


## Arduino
![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white)
![Espressif](https://img.shields.io/badge/espressif-E7352C.svg?style=for-the-badge&logo=espressif&logoColor=white)
![PlatformIO](https://img.shields.io/badge/PlatformIO-%23222.svg?style=for-the-badge&logo=platformio&logoColor=%23f5822a)
![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white)

In this Section we will talk about how to set up the Arduino Side of the Project.<br>

| This devices measures:|
| ------------- |
| Temperature | 
| Humidity |
| Heat Index | 
| Brightness Percentage |
| Voltage [(How?)](https://randomnerdtutorials.com/esp32-adc-analog-read-arduino-ide/) |


### Parts used:
| Item Name | Link to buy |
| ------------- |:------------:|
| ESP32 | [az-delievery.de](https://www.az-delivery.de/products/esp32-developmentboard?_pos=3&_sid=a493aef60&_ss=r) |
| Display | [az-delievery.de](https://www.az-delivery.de/products/1-3zoll-i2c-oled-display?_pos=4&_sid=442aa5388&_ss=r) |
| Temperature Sensor | [az-delievery.de](https://www.az-delivery.de/products/dht-11-temperatursensor-modul) |
| Kabel | [az-delievery.de](https://www.az-delivery.de/products/3er-set-40-stk-jumper-wire-m2m-f2m-f2f) |
| Light Sensor | [Amazon](https://amzn.eu/d/dLZuBOP) |
| Buttons | [Amazon](https://amzn.eu/d/5I6dd4j) |


### Circuit/Circuit Diagram/Schematic Diagram:<br>
<img src="https://i.imgur.com/tlFnFwq.png" width="50%">

This plan was translated to English from German. 
<br>For Full Image click [**this link**](https://i.imgur.com/tlFnFwq.png)

**Please note that you can change the Pins (except for the Display) in the Arduino Code.**

### How to install:
1. Install [VSCode](https://code.visualstudio.com/download) and [PlatformIO IDE](https://marketplace.visualstudio.com/items?itemName=platformio.platformio-ide)
2. Create a new Project and select these
    - Board: DOIT ESP32 DEVKIT V1
    - Framework: Arduino
3. Install these libaries to your Project:
    - Adafruit BusIO
    - Adafruit GFX Libary
    - Adafruit SSD1306
    - Adafruit Unified Sensor
    - DHT sensor libary
4. You can now insert the Code in **./src/main.cpp**

#### Used Port for the Arduino API: 4719

## Database
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
### I use SQLite as Database.

- I have for each measured value each 3 tables: "minutes", "hours" and "days". 
- Each table normally shouldnt hold more then about 120 rows.

- "Minutes" hold the values of every check by the Middleman-API. 
    - If the saved values get older then 2 minutes, they get averaged and saved under "hours".
    - The old values get deleted from minutes.

        -> This is to decrease Database size and space consumption.
- Every time unit has the same process. 
    - Minutes after 2 minutes of age -> averaged into hours
    - Hours after 2 days of age -> averaged into days
    - Days after |TODO| -> averaged into |TODO|

<br>

#### I use [SQLite Studio](https://sqlitestudio.pl/) for a better Overview of the Database.<br>I made using their "Export" feature, a file which you can use to create your own Database.
### The File is: [**db.sql**](./db.sql)
<br>

## Middleman-API
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

### The Middleman-API is made in Python with FastAPI and APScheduler.

APScheduler uses a "AsyncIOScheduler" to schedule a event which every minute queries current values from the Arduino API. The interval can be changed.
Right after recieving the new values it builds up a connection with the Database to average and delete old values and append the new values.

When the Webpage queries the values, the Python Script gets all the saved values from the requested type from the Database and returns it to the Webpage.

The Middleman could potentially quiery new values constantly from the Arduino. The Arduino refreshes his values constantly.

#### Used Port for the Middleman-API: 8000
<br>

## Webpage
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![Chart.js](https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white)

The Main part of the Site is split into 6 columms. One for each value being displayed.<br>
On the left there is a yet almost empty Sidebar and on the top a Header.

The values recieved from the Middleman-API are getting displayed in a Line Chart using Chart.js.<br>
Under each Chart are buttons to change the time unit.

Each Chart has a Min object for the X-Axis (time), so it wont display values older then a hour.<br>



## Settings
Using the Webpage you are able to adjust some settings on the Arduino.<br>
With a POST request you can change them to the opposite (toggle) or with a GET you can see the current state.

The Webpage also allows easier control of them.

Here is a Overview of them:
| | | |
|:--|:--|:--|
| | | |
