//var apiURL = "http://127.0.0.1:8000/"
var apiURL = "http://192.168.178.186:8000/"

const humidityData = [];
const temperatureData = [];
const heatIndexData = [];
const lightData = [];
const voltageData = [];
var humidityChart = Chart;
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
    refreshData("voltage", voltageData, voltageUnit.unit, "V");
}

function refreshAllCharts() {
    updateChart("Luftfeuchtigkeit in %", humidityData, humidityChart)
    updateChart("Temperatur in Celsius", temperatureData, temperatureChart)
    updateChart("Hitzeindex in Celsius", heatIndexData, heatIndexChart)
    updateChart("Helligkeit in %", lightData, lightChart)
    updateChart("Stromspannung in Volt (V)", voltageData, voltageChart)
}

function createAllCharts() {
    humidityChart = createChart("humidity", "Luftfeuchtigkeit in %", humidityData)
    temperatureChart = createChart("temperature", "Temperatur in Celsius", temperatureData)
    heatIndexChart = createChart("heatIndex", "Hitzeindex in Celsius", heatIndexData)
    lightChart = createChart("light", "Helligkeit in %", lightData)
    voltageChart = createChart("voltage", "Stromspannung in Volt (V)", voltageData)

    setInterval(refreshAll, (61 * 1000)); // Execute every 61 seconds
}

function changeUnit(name, unit, variable) {
    var oldUnit = variable.unit;
    variable.unit = unit;

    document.getElementById(name + "-" + oldUnit).style = "background: #4CAF50; font-weight: normal"; // Set to normal
    document.getElementById(name + "-" + unit).style = "background: #c7a302c2; font-weight: bold"; // Set to pressed
    refreshAllData();
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

    while(dataArray.length > 0) {
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

function updateChart(labelText, dataArray, chartObj) {
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

    chartObj.options.scales.x.time.min = Date.now() - (3600 * 1000); // unix timestamp in milisec from one hour ago
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
                  min: Date.now() - (3600 * 1000), // unix timestamp from one hour ago
                  displayFormats: {
                    second: 'HH:mm'
                  },
                  tooltipFormat: 'dd.MM.yyyy HH:mm:ss'
                },
                title: {
                    display: true,
                    text: 'Zeit'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Werte'
                }
            }
          },
        },
    });

    if (name != "voltage") {
        chartObj.options.scales.y.ticks.precision = 0;
    }

    return chartObj;
}