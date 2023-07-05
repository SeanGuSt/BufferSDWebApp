/*This just creates the initial graph we see on loading the page*/
var ctx = document.getElementById("chartCurve").getContext("2d");
var dataCurve = {
    datasets: [
        {
            type: 'scatter',
            label: 'Acid Titration',
            pointRadius: 2,
            hidden: true,
            data: [{x: 0, y: 0}]
        },
        {
            type: 'scatter',
            label: 'Base Titration',
            pointRadius: 4,
            hidden: true,
            data: [{ x: 0, y: 0 }]
        },
        {
            type: 'scatter',
            label: 'Water',
            pointRadius: 1,
            hidden: true,
            data: [{ x: 0, y: 0 }]
        },
        {
            type: 'line',
            label: 'Buffer Approx.',
            pointRadius: 0.1,
            hidden: true,
        },
        {
            type: 'line',
            label: 'Base Approx.',
            pointRadius: 0.1,
            hidden: true,
        }
    ]
};
var configCurve = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: {
            type: "linear",
            title: {
                display: true,
                text: "Volume Added (mL)"
            }
        },
        y: {
            title: {
                display: true,
                text: "pH"
            },
            min: 0,
            max: 14
        }
    }
};
var chartCurve = new Chart(ctx, {
    // The type of chart we want to create
    type: "line",
    // The data for our dataset
    data: dataCurve,
    //The configuration details for our graph
    options: configCurve
});
var cd = chartCurve.data.datasets;
function plotThing(results, index, doShow) {
    cd[index].data = results;
    chartCurve.setDatasetVisibility(index, doShow);
    chartCurve.update();
}
var htmlTable = document.getElementById("myTable");
function plotBC(fillcurve, oricurve, maxBC) {
    cd[0].data = oricurve;
    cd[0].label = 'Buffer Capacity Curve'
    cd[1].data = fillcurve;
    cd[1].label = 'Gap Filler'
    cd[1].pointRadius = 2
    chartCurve.options.scales = {
        x: {
            type: "linear",
            title: {
                display: true,
                text: "pH"
            },
            min: 0,
            max: 14
        },
        y: {
            title: {
                display: true,
                text: "Beta"
            },
            min: 0,
            max: 1.7*maxBC
        }
    };
    chartCurve.update();
}
function haveAllNeccesities() {
    if (!(cd[0].data.length>1 && cd[1].data.length>1)) {
        alert("Give Data!!!!");
        return false;
    }
    if (cd[2].data.length>1) {
        alert("Already Done!!!!");
        return false;
    }
    return true;
}
function tableSetup(newInput, rowInd, colInd) {
    var table = document.getElementById("myTable");
    table.rows[rowInd].cols[colInd].innerHTML = newInput;
}
function numberCleanup(sse, tBeta) {
    document.getElementById("sse").value = sse.toExponential(3);
    document.getElementById("tb").value = tBeta.toPrecision(4);
}