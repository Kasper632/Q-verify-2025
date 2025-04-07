document.getElementById("tableSearchInput").addEventListener("keyup", function () {
    const filter = this.value.toLowerCase();
    const rows = document.querySelectorAll(".filter-row");

    rows.forEach(row => {
        const competence = row.dataset.competences?.toLowerCase() || "";
        const pmnum = row.dataset.pmnum?.toLowerCase() || "";
        const cxline = row.dataset.cxlineroutenr?.toLowerCase() || "";
        const location = row.dataset.location?.toLowerCase() || "";
        const description = row.dataset.description?.toLowerCase() || "";
        const anomaly = row.dataset.anomalyfields?.toLowerCase() || "";

        const match = competence.includes(filter) ||
            pmnum.includes(filter) ||
            cxline.includes(filter) ||
            location.includes(filter) ||
            description.includes(filter) ||
            anomaly.includes(filter);

        row.style.display = match ? "" : "none";
    });
});


document.getElementById("toggleCorrect").addEventListener("change", function () {
    document.getElementById("correctSection").style.display = this.checked ? "" : "none";
});

document.getElementById("toggleErrors").addEventListener("change", function () {
    document.getElementById("errorSection").style.display = this.checked ? "" : "none";
});