var table = $('myTable');
table.oldHTML = table.innerHTML;
const finalLevel = 5;
const abCol = 2;
function setupTable(newtable) {
    if (programLevel == finalLevel) {
        const rowCount = newtable[0].length;
        for (i = 0; i < rowCount; i++) {
            var row = table.insertRow(-1);
            for (j = 0; j < 4; j++) {
                let col = row.insertCell(j);
                col.innerHTML = newtable[j][i];
                if (j != abCol) {
                    col.innerHTML = Number(col.innerHTML).toFixed(4);
                }
            }
        }
    }
}
function numberCleanup(elementid, value, preexp = 4) {
    if (preexp < 0) { x = value.toExponential(-preexp); }
    else { x = value.toPrecision(preexp); }
    $(elementid).value = x;
}
function abSwap(e) {
    var cell = e.target.closest('td');
    if (!cell) { return [false, false]; } // Quit, not clicked on a cell
    if (cell.innerHTML === "a") {
        cell.innerHTML = "b";
        return [cell.parentNode.rowIndex-1, "b"];
    }
    else if (cell.innerHTML === "b") {
        cell.innerHTML = "a";
        return [cell.parentNode.rowIndex-1, "a"];
    }
    else {
        return [false, false];
    }
}