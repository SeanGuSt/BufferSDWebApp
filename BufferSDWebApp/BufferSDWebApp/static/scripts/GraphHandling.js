/*This just creates the initial graph we see on loading the page*/
var ctx = document.getElementById("chartCurve").getContext("2d");
const defaultScales = {
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
};
var dataCurve = {
    datasets: [
        {
            type: 'scatter',
            label: 'Acid Titration',
            pointRadius: 2,
            hidden: true,
            data: [{ x: 0, y: 0 }]
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
            label: 'Buffer Capacity Curve',
            pointRadius: 2,
            hidden: true,
            data: [{ x: 0, y: 0 }]
        },
        {
            type: 'scatter',
            label: 'Gap Filler',
            pointRadius: 2,
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
            label: 'Water Approx.',
            pointRadius: 0.1,
            hidden: true,
        }
    ]
};
var configCurve = {
    responsive: true,
    maintainAspectRatio: false,
    scales: defaultScales
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

function plotThing(results, index, doShow = true) {
    cd[index].data = results;
    chartCurve.setDatasetVisibility(index, doShow);
    chartCurve.update();
}
function plotBC(fillcurve, currentcurve, maxBC) {
    chartCurve.setDatasetVisibility(0, false);
    chartCurve.setDatasetVisibility(1, false);
    cd[2].data = currentcurve;
    cd[3].data = fillcurve;
    chartCurve.setDatasetVisibility(2, true);
    chartCurve.setDatasetVisibility(3, true);
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