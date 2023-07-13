/*This just creates the initial graph we see on loading the page*/
var ctx = document.getElementById("chartCurve").getContext("2d");
var programLevel = 0;
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
function programAtLevel(x) {
    return programLevel == x;
}
function programAtLeastLevel(x) {
    return programLevel >= x;
}
var table = document.getElementById('myTable');
table.oldHTML = table.innerHTML;
function changeProgramLevel(newLevel) {
    /*0:   Nothing has happened
      1:   Parameters added
      2:   Acid data added
      3:   Base data added
      4:   Curve generated and gaps filled
      4.3: Graph shifted horizontally
      4.5: Beginning trimmed
      4.8: Ending trimmed
      5:   Curve modeled*/
    if (newLevel <= programLevel) {
        switch (newLevel) {
            case 0://Clear All selected
                document.getElementById("paramFile").value = null
                document.getElementById("paramDefaults").checked = false
                document.getElementById("ingredient").value = "";
                document.getElementById("conTitr").value = "";
                document.getElementById("HCl").value = "";
                document.getElementById("NaOH").value = "";
                document.getElementById("Init_Vol").value = "";
                document.getElementById("NaClpercent").value = "";
            case 1://New parameters introduced
                document.getElementById("acid_titr_button").value = null
            case 2://New acid .RPT file introduced
                document.getElementById("base_titr_button").value = null
            case 3://New base .RPT file introduced
                if (newLevel == 3) { chartCurve.setDatasetVisibility(0, true) }
                chartCurve.setDatasetVisibility(2, false);
                chartCurve.setDatasetVisibility(3, false);
                chartCurve.setDatasetVisibility(4, false);
                chartCurve.options.scales = defaultScales;
            case 4://Curve regenerated and gaps refilled
                document.getElementById("electrode_shift").value = 0;
            case 4.3://pH shift
                document.getElementById("Trim_beg").value = 0;
                document.getElementById("Trim_end").value = 0;
            case 4.5://Beginning points retrimmed
            case 4.8://Ending points retrimmed
                chartCurve.setDatasetVisibility(5, false);
                chartCurve.setDatasetVisibility(6, false);
                table.innerHTML = table.oldHTML;
                document.getElementById("sse").value = "";
                document.getElementById("eph").value = "";
                document.getElementById("adjc").value = "";
                document.getElementById("tb").value = "";
            case 5:

        }
        chartCurve.update();
    }
    programLevel = newLevel;
}
const finalLevel = 5;
const abCol = 2
function setupTable(newTable) {
    if (programLevel == finalLevel) {
        var newtable = transpose(newTable);
        const rowCount = newtable.length;
        for (i = 0; i < rowCount; i++) {
            var row = table.insertRow(-1);
            for (j = 0; j < 4; j++) {
                var col = row.insertCell(j);
                col.innerHTML = newtable[j][i];
                if (j != abCol) {
                    col.innerHTML = col.innerHTML.toFixed(4);
                }
            }
        }
    }
}
function transpose(matrix) {
    return matrix[0].map((col, i) => matrix.map(row => row[i]));
}
function numberCleanup(elementid, value, preexp = 4) {
    if (preexp < 0) { x = value.toExponential(-preexp); }
    else { x = value.toPrecision(preexp); }
    document.getElementById(elementid).value = x;
}
function abSwap(e) {
    var cell = e.target.closest('td');
    if (!cell) { return false; } // Quit, not clicked on a cell
    if (cell.innerHTML === "a") {
        cell.innerHTML = "b";
        return [cell.cellIndex, "b"];
    }
    else if (cell.innerHTML === "b") {
        cell.innerHTML = "a";
        return [cell.cellIndex, "a"];
    }
    else {
        return false;
    }
}