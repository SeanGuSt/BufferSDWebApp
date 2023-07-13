function trimSettings(clicked_button) {
    if (document.getElementById("Trim_beg").readOnly) {
        document.getElementById("Trim_beg").readOnly = false;
        document.getElementById("Trim_end").readOnly = false;
        document.getElementById("Trim_beg").style.backgroundColor = "transparent";
        document.getElementById("Trim_end").style.backgroundColor = "transparent";
        document.getElementById("trim_domain_button").style.backgroundColor = "lightgray";
    } else {
        document.getElementById("Trim_beg").readOnly = true;
        document.getElementById("Trim_end").readOnly = true;
        document.getElementById("Trim_beg").style.backgroundColor = "lightgray";
        document.getElementById("Trim_end").style.backgroundColor = "lightgray";
        document.getElementById("trim_domain_button").style.backgroundColor = "#f0f0f0";
    }
};
function buttonColorSwap(clicked_button) {
    if (clicked_button.style.backgroundColor == "#f0f0f0") {
        clicked_button.style.backgroundColor = "lightgray";
    } else {
        clicked_button.style.backgroundColor = "#f0f0f0";
    }
};
function buttonColorChange(clicked_id, newColor) {
    document.getElementById(clicked_id).style.backgroundColor = newColor;
}