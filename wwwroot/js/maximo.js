document.addEventListener("DOMContentLoaded", function () {
    // Redigeringsfunktionalitet
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", function () {
            let row = this.closest("tr");

            document.querySelectorAll("tr").forEach(otherRow => {
                if (otherRow !== row && otherRow.querySelector(".save-btn") && !otherRow.querySelector(".save-btn").classList.contains("d-none")) {
                    resetRow(otherRow);
                }
            });

            row.querySelectorAll(".text").forEach(el => el.classList.add("d-none"));
            row.querySelectorAll("input").forEach(el => el.classList.remove("d-none"));

            row.querySelector(".save-btn").classList.remove("d-none");
            row.querySelector(".cancel-btn").classList.remove("d-none");
            this.classList.add("d-none");

            // Dölj papperskorgen efter att ha klickat på pennan
            row.querySelector(".bi-trash").closest("button").classList.add("d-none");
        });
    });

    // Funktionalitet för avbrytknappen (återställ till ursprungligt tillstånd)
    document.querySelectorAll(".cancel-btn").forEach(button => {
        button.addEventListener("click", function () {
            let row = this.closest("tr");

            // Återställ text och fält
            resetRow(row);
        });
    });

    // Funktion för att återställa en rad till sitt ursprungliga tillstånd
    function resetRow(row) {
        // Återställ text och dolda fält
        row.querySelectorAll(".text").forEach(el => el.classList.remove("d-none"));
        row.querySelectorAll("input").forEach(el => el.classList.add("d-none"));

        row.querySelector(".save-btn").classList.add("d-none");
        row.querySelector(".edit-btn").classList.remove("d-none");
        row.querySelector(".cancel-btn").classList.add("d-none");

        row.querySelector(".bi-trash").closest("button").classList.remove("d-none");
    }

    // Funktion för att visa bekräftelseknappar vid klick på papperskorgen
    document.querySelectorAll(".btn-sm.btn-custom").forEach(button => {
        button.addEventListener("click", function () {
            if (this.querySelector(".bi-trash")) {
                let row = this.closest("tr");

                document.querySelectorAll("tr").forEach(otherRow => {
                    if (otherRow !== row && otherRow.querySelector(".confirm-yes") && !otherRow.querySelector(".confirm-yes").classList.contains("d-none")) {
                        cancelDelete(otherRow.querySelector(".confirm-no"));
                    }
                });

                this.classList.add("d-none");
                row.querySelector(".confirm-yes").classList.remove("d-none");
                row.querySelector(".confirm-no").classList.remove("d-none");
            }
        });
    });

    // Funktion för att bekräfta borttagning och ta bort raden
    function confirmDelete(button) {
        let row = button.closest("tr");

        row.remove();
    }

    // Funktion för att avböja borttagning och återställa till ursprungligt tillstånd
    function cancelDelete(button) {
        let row = button.closest("tr");

        row.querySelector(".bi-trash").closest("button").classList.remove("d-none");
        row.querySelector(".confirm-yes").classList.add("d-none");
        row.querySelector(".confirm-no").classList.add("d-none");
    }

    document.querySelectorAll(".confirm-yes").forEach(button => {
        button.addEventListener("click", function () {
            confirmDelete(this);
        });
    });

    document.querySelectorAll(".confirm-no").forEach(button => {
        button.addEventListener("click", function () {
            cancelDelete(this);
        });
    });
});