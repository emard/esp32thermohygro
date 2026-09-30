function makeeditable(table) {
    for (let i = 0; i < table.rows.length; i++) {
        for (let j = 0; j < table.rows[i].cells.length; j++) {
            // with contenteditable in each cell, it is possible to navigate through them with tab key
            table.rows[i].cells[j].setAttribute("contenteditable", "true");
        }
    }
}

function addpastelistener(table) {
    table.addEventListener('paste', (event) => {
        event.preventDefault();
        let paste = (event.clipboardData || window.clipboardData).getData('text');
        let col = event.target;
        while (col && col.tagName != 'TD') col = col.parentElement;
        let row = col;
        while (row && row.tagName != 'TR') row = row.parentElement;
        let tab = row;
        while (tab && tab.tagName != 'TBODY' && tab.tagName != 'TABLE') tab = tab.parentElement;
        let rows = paste.replace(/(\r\n)|\r|\n/g, '\n').split("\n");
        for (let i = 0, r = row.rowIndex; i < rows.length && r < table.rows.length; i++) {
            let cells = rows[i].split("\t");
            for (let j = 0, c = col.cellIndex; j < cells.length && c < table.rows[r].cells.length; j++) {
                table.rows[r].cells[c].innerHTML = cells[j].trim();
                c++;
            }
            r++;
        }
    });
}

function init() {
    const editabletables = document.getElementsByClassName('editabletable');
    for (let i = 0; i < editabletables.length; i++) {
        makeeditable(editabletables[i]);
        addpastelistener(editabletables[i]);
    }
}

init();
