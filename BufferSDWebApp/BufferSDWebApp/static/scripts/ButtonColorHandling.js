function trimSettings(clicked_button) {
    if (document.getElementById("trim_beginning").readOnly) {
        document.getElementById("trim_beginning").readOnly = false;
        document.getElementById("trim_end").readOnly = false;
        document.getElementById("trim_beginning").style.backgroundColor = "transparent";
        document.getElementById("trim_end").style.backgroundColor = "transparent";
        document.getElementById("trim_domain_button").style.backgroundColor = "lightgray";
    } else {
        document.getElementById("trim_beginning").readOnly = true;
        document.getElementById("trim_end").readOnly = true;
        document.getElementById("trim_beginning").style.backgroundColor = "lightgray";
        document.getElementById("trim_end").style.backgroundColor = "lightgray";
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