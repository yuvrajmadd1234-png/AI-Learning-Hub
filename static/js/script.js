document.addEventListener("DOMContentLoaded", function () {

    const search = document.getElementById("courseSearch");

    if (search) {

        search.addEventListener("keyup", function () {

            const value = this.value.toLowerCase();

            const rows = document.querySelectorAll("tbody tr");

            rows.forEach(row => {

                const text = row.innerText.toLowerCase();

                if (text.includes(value)) {

                    row.style.display = "";

                } else {

                    row.style.display = "none";

                }

            });

        });

    }

});