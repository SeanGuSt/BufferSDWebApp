var $ = function (id) { return document.getElementById(id); };
var programLevel = 0;
var table = $('myTable');
table.oldHTML = table.innerHTML;
function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}
function setReadOnly(field_id, isReadOnly) {
    var field = $(field_id);
    field.readOnly = isReadOnly;
    if (!isReadOnly) {
        field.style.backgroundColor = "transparent";
    }
    else {
        field.style.backgroundColor = "lightgray";
        if (isNumeric(field.value)) {
            field.value = 0;
        }
        else {
            field.value = null;
        }
    }
}
function programAtLevel(x) {
    return programLevel == x;
}
function programAtLeastLevel(x) {
    return programLevel >= x;
}
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
                $("paramFile").value = null;
                $("paramDefaults").checked = false;
                $("ingredient").value = null;
                $("conTitr").value = null;
                $("HCl").value = null;
                $("NaOH").value = null;
                $("Init_Vol").value = null;
                $("NaClpercent").value = null;
            case 1://New parameters introduced
                if (!Number($("NaOH").value) && !$("paramDefaults").checked) {
                    setReadOnly("acid_titr_button", true);
                }
                chartCurve.setDatasetVisibility(0, false);
                setReadOnly("base_titr_button", true);
            case 2://New acid .RPT file introduced
                chartCurve.setDatasetVisibility(1, false);
                $("base_titr_button").value = null;
            case 3://New base .RPT file introduced
                if (newLevel == 3) { chartCurve.setDatasetVisibility(0, true); }
                chartCurve.setDatasetVisibility(2, false);
                chartCurve.setDatasetVisibility(3, false);
                chartCurve.setDatasetVisibility(4, false);
                chartCurve.options.scales = defaultScales;
                setReadOnly("electrode_shift", true);
                setReadOnly("Trim_beg", true);
                setReadOnly("Trim_end", true);
            case 4://Curve regenerated and gaps refilled
                $("electrode_shift").value = 0;
                $("Trim_beg").value = 0;
                $("Trim_end").value = 0;
            case 4.3://pH shift
            case 4.5://Beginning points retrimmed
            case 4.8://Ending points retrimmed
                chartCurve.setDatasetVisibility(5, false);
                chartCurve.setDatasetVisibility(6, false);
                table.innerHTML = table.oldHTML;
                $("sse").value = "";
                $("eph").value = "";
                $("adjc").value = "";
                $("tb").value = "";
            case 5:

        }
        chartCurve.update();
    }
    else {
        switch (newLevel) {
            case 5:
            case 4.8:
            case 4.5:
            case 4.3:
            case 4:
                setReadOnly("electrode_shift", false);
                setReadOnly("Trim_beg", false);
                setReadOnly("Trim_end", false);
            case 3:
            case 2:
                setReadOnly("base_titr_button", false);
            case 1:
                setReadOnly("acid_titr_button", false);
            case 0:
        }
    }
    programLevel = newLevel;
}
