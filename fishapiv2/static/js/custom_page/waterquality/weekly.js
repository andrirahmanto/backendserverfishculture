/**
 *
 * You can write your JS code here, DO NOT touch the default style file
 * because it will make it harder for you to update.
 *
 */

"use strict";

$(document).ready(function () {
    // Setup - add a text input to each footer cell
    $('#mainTable tfoot th').each(function () {
        var title = $(this).text();
        $(this).html('<input type="text" placeholder="Search ' + title + '" />');
    });

    DataTable
    var table = $('#mainTable').DataTable({
        initComplete: function () {
            this.api()
                .columns()
                .every(function () {
                    var column = this;
                    var select = $('<select><option value=""></option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex($(this).val());

                            column.search(val ? '^' + val + '$' : '', true, false).draw();
                        });

                    column
                        .data()
                        .unique()
                        .sort()
                        .each(function (d, j) {
                            select.append('<option value="' + d + '">' + d + '</option>');
                        });
                    // Menghitung rata-rata pada kolom
                    var footer = $(column.footer());
                    var data = column.data();

                    var average = data
                        .reduce(function (acc, curr) {
                            return acc + parseFloat(curr);
                        }, 0) / data.length;

                    var total = data
                        .reduce(function (acc, curr) {
                            return acc + parseFloat(curr);
                        }, 0);

                    if (column.index() == 6 || column.index() == 7 || column.index() == 8 || column.index() == 9 || column.index() == 10) {

                        if (isNaN(average) == false) {
                            footer.html(footer.html() + '<br> <br>' + ' Avg: ' + average.toFixed(2) + '');
                        }
                    }
                });
        },
    });
    $("#form-date").datepicker({
        format: "yyyy-mm",
        startView: "months",
        minViewMode: "months"
    });
});


function setDate() {
    let date = document.getElementById("form-date").value;
    let link = document.getElementById("link-root").value;
    window.location.href = `${link}${date}`
}