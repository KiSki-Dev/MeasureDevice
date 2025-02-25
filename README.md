> [!IMPORTANT]
> **Unfinished** -> Please note that this repository is not finished yet. Please wait until finished before usage.

# "MeasureDevice" using Arduino, API, Database and Webpage
## This is a small Project, I made during my two-week long student Internship at [Janitza](https://www.janitza.com/).
----

1. An Arduino attachted with multiple sensors reads multiple values like light, temperature and more. 
2. A FastAPI queries the Arduino every mintue for these values. 
3. The FastAPI saves them in a SQLite Database and checks the entire database for old values, which then get averaged and saved in a new table to decrease the Database Size. 
4. A webpage queries the FastAPI for the Values saved in the Database and shows them nice in Charts. 
5. The webpage also allows you to adjust settings from the Arduino.

#### If you dont understand this explanation, this Plan might help you understand:
![alt text](./CommunicationPlan.svg "Communication Plan Diagram")

----

| Category      | Jump to Category |
| ------------- |:-------------:|
| Arduino       | [:one:](#arduino) |
| Middleman-API | [:two:](#middleman-api)      |
| Webpage       | [:three:](#webpage)      |
| Settings      | [:four:](#settings)      |


## Arduino
In this Section we will talk about how to set up the Arduino Side of the Project.
<br>

The Script currently allows to measure:
| Measures      | Sensor |
| ------------- |:------------:|
| Temperature | [Link to Sensor](https://sensorkit.joy-it.net/en/sensors/ky-015) |
| Humidity | Same sensor as Temperature |
| Heat Index | Same sensor as Temperatture |
| Brightness Percentage | [Link to Sensor](https://amzn.eu/d/iABgUTF) |
| Voltage | No addition needed. [How?](https://randomnerdtutorials.com/esp32-adc-analog-read-arduino-ide/) |


## Middleman-API

## Webpage

## Settings

![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white)
![Espressif](https://img.shields.io/badge/espressif-E7352C.svg?style=for-the-badge&logo=espressif&logoColor=white)


![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PlatformIO](https://img.shields.io/badge/PlatformIO-%23222.svg?style=for-the-badge&logo=platformio&logoColor=%23f5822a)

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white)

![Chart.js](https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white)