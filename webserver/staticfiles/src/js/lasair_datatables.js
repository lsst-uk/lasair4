document.addEventListener('DOMContentLoaded', function() {

    let dataTableEls = d.querySelectorAll('.datatable');
    dataTableEls.forEach(function(dataTableEl) {
        if (dataTableEl) {

            const dataTable = new simpleDatatables.DataTable(dataTableEl, {
                labels: {
                    placeholder: "Search table...",
                    perPage: "{select} rows per page",
                    noRows: "No objects found",
                    info: "Showing {start} to {end} of {rows} rows",
                },
                layout: {
                    top: "{search}",
                    bottom: "{select}{info}{pager}"
                },
                perPage: 100,
                perPageSelect: [10, 50, 100, 500, 10000]
            });

            const headings = dataTable.columns().dt.labels;

            if (headings.includes("objectId")) {
                const idx = headings.indexOf("objectId");
                dataTable.columns().sort(idx, "desc")
            } else if (headings.includes("Created")) {
                const idx = headings.indexOf("Created");
                dataTable.columns().sort(idx, "desc")
            }
            // console.log(dataTable.columns().dt.labels);

            document.querySelectorAll(".export").forEach(function(el) {
                el.addEventListener("click", function(e) {
                    var type = el.dataset.type;

                    var filename = el.dataset.filename;

                    if (filename == null) {
                        filename = "lasair-export";
                    }

                    console.log("HERE:", filename);

                    var data = {
                        type: type,
                        filename: filename,
                    };

                    if (type === "csv") {
                        data.columnDelimiter = ",";
                    }

                    dataTable.export(data);
                });
            });

        }
    });

});
