var apiURL = "http://:8000/" // URL of the Middleman API

const humidityData = [];
const temperatureData = [];
const heatIndexData = [];
const lightData = [];
const voltageData = [];

var humidityChart;
var temperatureChart;
var heatIndexChart;
var lightChart;
var voltageChart;

var humidityUnit = {unit : "Min"};
var temperatureUnit = {unit : "Min"};
var heatIndexUnit = {unit : "Min"};
var lightUnit = {unit : "Min"};
var voltageUnit = {unit : "Min"};

async function refreshAll() {
    await refreshAllData();
    await refreshAllCharts();
}

async function refreshAllData() {
    console.log(new Date().toLocaleTimeString())
    refreshData("humidity", humidityData, humidityUnit.unit, "%");
    refreshData("temperature", temperatureData, temperatureUnit.unit, "°C");
    refreshData("heatIndex", heatIndexData, heatIndexUnit.unit, "°C");
    refreshData("light", lightData, lightUnit.unit, "%");
    await refreshData("voltage", voltageData, voltageUnit.unit, "V");
}

function refreshAllCharts() {
    updateChart("Luftfeuchtigkeit in %", humidityData, humidityChart, humidityUnit.unit)
    updateChart("Temperatur in Celsius", temperatureData, temperatureChart, temperatureUnit.unit)
    updateChart("Hitzeindex in Celsius", heatIndexData, heatIndexChart, heatIndexUnit.unit)
    updateChart("Helligkeit in %", lightData, lightChart, lightUnit.unit)
    updateChart("Stromspannung in Volt (V)", voltageData, voltageChart, voltageUnit.unit)
}

async function createAllCharts() {
    humidityChart = createChart("humidity", "Luftfeuchtigkeit in %", humidityData)
    temperatureChart = createChart("temperature", "Temperatur in Celsius", temperatureData)
    heatIndexChart = createChart("heatIndex", "Hitzeindex in Celsius", heatIndexData)
    lightChart = createChart("light", "Helligkeit in %", lightData)
    voltageChart = await createChart("voltage", "Stromspannung in Volt (V)", voltageData)

    setInterval(refreshAll, (61 * 1000)); // Execute every 61 seconds

    await refreshAll();
}

function changeUnit(name, unit, variable) {
    var oldUnit = variable.unit;
    variable.unit = unit;

    document.getElementById(name + "-" + oldUnit).style = "background: #4CAF50; font-weight: normal"; // Set to normal
    document.getElementById(name + "-" + unit).style = "background: #c7a302c2; font-weight: bold"; // Set to pressed
    
    refreshAll();
}

async function refreshData(name, dataArray, selectedTime, unit) {
    var rawData;

    document.getElementById("text-" + name).innerHTML = "Refreshing Data...";
    await fetch(apiURL + name + selectedTime, {
        method: "GET",
      })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        var jsonData = JSON.stringify(data);
        rawData = JSON.parse(jsonData);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    })

    while(dataArray.length != 0) {
        dataArray.pop(); // Clear Array before refilling it
    }
    for (var i = 0; i < rawData.length; i++){
        var obj = rawData[i];
        dataArray.push({"x": obj[1] * 1000, "y": obj[0]});
    }

    const lastObj = rawData[rawData.length - 1];
    console.log(name + ": " + String(lastObj))
    var date = new Date(lastObj[1] * 1000);
    var dateOptions = { day: "2-digit", month: "2-digit", year: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" };
    var formattedDate = date.toLocaleString("de-DE", dateOptions);

    document.getElementById("text-" + name).innerHTML = `${parseInt(rawData[0])}${unit} checked at ${formattedDate}.`;
}

function updateChart(labelText, dataArray, chartObj, unit) {
    //console.log(dataArray);
    const data = { 
        datasets: [{
            label: labelText,
            data: dataArray,
            backgroundColor: "#ff4f4f",
            borderColor: "#eb0202",
            fill: false
        }]
    };

    if (unit == "Min") {
        chartObj.options.scales.x.time.displayFormats.second = 'HH:mm';
        chartObj.options.scales.x.min = Date.now() - (60 * 60 * 1000); // 60 minutes in ms
    }
    else if (unit == "Hour") {
        chartObj.options.scales.x.time.unit = "minute";
        chartObj.options.scales.x.time.displayFormats.minute = 'HH:mm';
        chartObj.options.scales.x.min = Date.now() - (24 * 60 * 60 * 1000); // 24 hours in ms
    }

    else if (unit == "Day") {
        chartObj.options.scales.x.time.unit = "hour";
        chartObj.options.scales.x.time.displayFormats.hour = 'dd.MM';
        chartObj.options.scales.x.min = Date.now() - (7 * 24 * 60 * 60 * 1000); // 7 days in ms
    }

    else if (unit == "Month") {
        chartObj.options.scales.x.time.unit = "month";
        chartObj.options.scales.x.time.displayFormats.hour = 'dd.MM.yyyy';
        chartObj.options.scales.x.min = ""; // no limit for months to avoid waiting time
    }

    chartObj.data.datasets[0].data[data.length - 1] = dataArray[dataArray.length - 1];
    chartObj.update();
}

function createChart(name, labelText, dataArray) {
    //console.log(dataArray);

    const data = { 
        datasets: [{
            label: labelText,
            data: dataArray,
            backgroundColor: "#ff4f4f",
            borderColor: "#eb0202",
            fill: false
        }]
    };

    var chartElement = document.getElementById(name + 'Chart').getContext('2d');
    var chartObj = new Chart(chartElement, {
        type: "line", 
        data: data,
        options: {
          legend: {display: true},
          scales: {
            x: {
                type: 'time',
                time: {
                  unit: 'second',
                  displayFormats: {
                    second: 'HH:mm'
                  },
                  tooltipFormat: 'dd.MM.yyyy HH:mm:ss'
                },
                min: Date.now() - (60 * 60 * 1000), // 60 minutes in ms
                title: {
                    display: true,
                    text: 'Zeit'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Werte'
                },
                ticks: {
                    precision: 1
                }
            }
          },
        },
    });

    return chartObj;
}