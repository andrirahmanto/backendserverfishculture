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

    // DataTable
    var table = $('#mainTable').DataTable({
        initComplete: function () {
            // Apply the search
            this.api()
                .columns()
                .every(function () {
                    var that = this;

                    $('input', this.footer()).on('keyup change clear', function () {
                        if (that.search() !== this.value) {
                            that.search(this.value).draw();
                        }
                    });
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