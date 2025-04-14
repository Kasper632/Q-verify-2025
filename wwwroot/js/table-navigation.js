function setupPagination(tableId, rowsPerPageSelector, prevBtnId, nextBtnId) {
    let currentPage = 1;
    let rowsPerPage = parseInt(document.getElementById(rowsPerPageSelector).value);
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll("tbody tr");

    function updateTable() {
        const totalRows = rows.length;
        const totalPages = Math.ceil(totalRows / rowsPerPage);
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        rows.forEach((row, i) => {
            row.style.display = (i >= start && i < end) ? "" : "none";
        });

        document.getElementById(prevBtnId).style.opacity = currentPage === 1 ? 0.4 : 0.6;
        document.getElementById(nextBtnId).style.opacity = currentPage === totalPages ? 0.4 : 0.6;
    }

    document.getElementById(rowsPerPageSelector).addEventListener("change", function () {
        rowsPerPage = parseInt(this.value);
        currentPage = 1;
        updateTable();
    });

    document.getElementById(prevBtnId).addEventListener("click", function () {
        if (currentPage > 1) {
            currentPage--;
            updateTable();
        }
    });

    document.getElementById(nextBtnId).addEventListener("click", function () {
        const totalPages = Math.ceil(rows.length / rowsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            updateTable();
        }
    });

    updateTable();
}

function waitForTableAndSetupPagination(tableId, rowsPerPageSelector, prevBtnId, nextBtnId) {
    const interval = setInterval(() => {
        const table = document.getElementById(tableId);
        if (table && table.querySelectorAll("tbody tr").length > 0) {
            clearInterval(interval);  
            setupPagination(tableId, rowsPerPageSelector, prevBtnId, nextBtnId);  
        }
    }, 500); 
}

document.addEventListener("DOMContentLoaded", function () {
    
    if (document.getElementById("anomalyTable")) {
        waitForTableAndSetupPagination("anomalyTable", "rowsPerPage", "prevPage", "nextPage");
    }
    if (document.getElementById("correctTable")) {
        waitForTableAndSetupPagination("correctTable", "rowsPerPageCorrect", "prevPageCorrect", "nextPageCorrect");
    }
    if (document.getElementById("errorTable")) {
        waitForTableAndSetupPagination("errorTable", "rowsPerPageError", "prevPageError", "nextPageError");
    }
});
