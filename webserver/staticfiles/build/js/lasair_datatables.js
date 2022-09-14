document.addEventListener('DOMContentLoaded', function() {

    let dataTableEls = d.querySelectorAll('.datatable');
    dataTableEls.forEach(function(dataTableEl) {
        if (dataTableEl) {
            const dataTable = new simpleDatatables.DataTable(dataTableEl, {
                columns: [
                    // Sort the second column in ascending order
                    {
                        select: 0,
                        sort: "desc"
                    }
                ],
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

            document.querySelectorAll(".export").forEach(function(el) {
                el.addEventListener("click", function(e) {
                    var type = el.dataset.type;

                    var data = {
                        type: type,
                        filename: "my-" + type,
                    };

                    if (type === "csv") {
                        data.columnDelimiter = "|";
                    }

                    dataTable.export(data);
                });
            });

        }
    });

});
