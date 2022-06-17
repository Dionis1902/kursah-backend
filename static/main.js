let charts = {}
let main = null
let mainChart = null


let info = {
    home_temperature: {
        end: '°C',
        name: 'Home Temperature'
    },
    outdoor_temperature: {
        end: '°C',
        name: 'Outdoor Temperature'
    },
    home_humidity: {
        end: '%',
        name: 'Home Humidity'
    },
    outdoor_humidity: {
        end: '%',
        name: 'Outdoor Humidity'
    },
    co2: {
        end: 'ppm',
        name: 'Carbon Dioxide Level'
    },
    pressure: {
        end: 'hPa',
        name: 'Pressure'
    }
}

function getSmallChart(data, id, color) {
    let properties = {
        series: [{
            name: info[id].name,
            data: data
        }],

        colors: [color],
        chart: {
            height: 80,
            type: 'area',
            toolbar: {
                show: false
            },
            zoom: {
                enabled: false
            },
            events: {
                  beforeZoom: function(ctx) {
                    ctx.w.config.xaxis.range = undefined
                  }
                }
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth'
        },
        yaxis: {
            show: false
        },
        xaxis: {
            labels: {
                show: false
            },
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false,
            },
            range: 600000
        },
        tooltip: {
            enabled: false
        },
        grid: {
            show: false
        },
        legend: {
            show: false
        },
        hover: {
            mode: null
        },
        noData: {
            text: 'Loading...'
        }

    }
    charts[id] = new ApexCharts(document.querySelector("#" + id + "_chart"), properties)
    charts[id].render()
}

function getMainChart() {
    let properties = {
        series: [{
            data: []
        }],
        chart: {
            height: '100%',
            type: 'area',
            toolbar: {
                show: true
            },
            zoom: {
                enabled: true
            }

        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth'
        },
        xaxis: {
            type: 'datetime',
            labels: {
                show: false,
                datetimeUTC: false
            },
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false,
            },tooltip: {
                enabled: false
            }
        },
        noData: {
            text: 'Loading...'
        }
    }
    mainChart = new ApexCharts(document.querySelector("#main_chart"), properties)
    mainChart.render()
}

function changeMainChart(id) {
    main = id

    document.getElementById('main_icon').className = document.getElementById(id + '_icon').className
    document.getElementById('main_icon').style.color = charts[id].opts.colors[0]
    document.getElementById('main_data').innerText = document.getElementById(id + '_data').innerText
    document.getElementById('main_end').innerText = document.getElementById(id + '_end').innerText
    document.getElementById('main_name').innerText = info[id].name

    mainChart.updateSeries(charts[id].opts.series)
    mainChart.updateOptions({
        chart: {
            events: {
                  beforeZoom: function(ctx) {
                    ctx.w.config.xaxis.range = undefined
                  }
                }
        },
        yaxis: {
            show: true,
            labels: {
                formatter: (value) => ["pressure", "co2"].includes(main) ? parseInt(value) : value.toFixed(2) + ' ' + info[id].end,
            }
        },
        xaxis: {
            range: 3600000
        },
        colors: charts[id].opts.colors,
        tooltip: {
            enabled: true,
            x: {
                show: true,
                format: 'yyyy-MM-dd HH:mm:ss'
            },
            marker: {
                show: false,
            },
            onDatasetHover: {
                highlightDataSeries: false
            },
            y: {
                formatter: (value) => value + ' ' + info[main].end
            }
        }
    })
}

function number_to(id, to, isInt = false, duration = 1000) {
    $('#' + id + '_data').animate({
        countNum: to
    }, {
        duration: duration,
        easing: 'swing',
        step: function () {
            $(this).text(isInt ? Math.floor(this.countNum) : Number(this.countNum).toFixed(2));
        },
        complete: function () {
            $(this).text(isInt ? this.countNum : this.countNum.toFixed(2));
        }
    })
}


function updateData(data) {
    for (let id of Object.keys(data)) {
        if (id === "time")
            continue
        number_to(id, data[id], ["pressure", "co2"].includes(id))
        charts[id].appendData([{
            name: info[id].name,
            data: [[data['time'], data[id]]]
        }])
    }
    number_to('main', data[main], ["pressure", "co2"].includes(main))
    mainChart.appendData([{
        name: info[main].name,
        data: [[data['time'], data[main]]]
    }])
}


document.addEventListener("DOMContentLoaded", () => {
    getMainChart()
    changeMainChart('home_temperature')
    document.getElementsByTagName('select')[0].onchange = (e) => changeMainChart(e.target.value)

    const socket = new WebSocket('ws://' + location.host + '/')

    socket.addEventListener('message', ev => {
        updateData(JSON.parse(ev.data))
    })

    socket.addEventListener('open', ev => {
        socket.send('innit|web')
    })
})