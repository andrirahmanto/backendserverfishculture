/**
 *
 * You can write your JS code here, DO NOT touch the default style file
 * because it will make it harder for you to update.
 *
 */

"use strict";

var ctx = document.getElementById("myChart").getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ["January", "February", "March", "April", "May", "June", "July", "August"],
        datasets: [
            {
                label: 'Nila Merah',
                data: [0.4, 1.1, 2, 2.1, 3.2, 3.4, 4, 4.3],
                borderWidth: 2,
                borderWidth: 2,
                backgroundColor: 'transparent',
                borderColor: 'rgba(254,86,83,.7)',
                pointBorderWidth: 0,
                pointRadius: 3.5,
                pointBackgroundColor: 'rgba(254,86,83,.7)',
                pointHoverBackgroundColor: 'rgba(254,86,83,.8)',
            },
            {
                label: 'Nila Hitam',
                data: [0.4, 0.6, 3, 3.1, 3.8, 4, 4.3, 4.6],
                borderWidth: 2,
                borderWidth: 2,
                backgroundColor: 'transparent',
                borderColor: 'rgba(0, 0, 0, 1)',
                pointBorderWidth: 0,
                pointRadius: 3.5,
                pointBackgroundColor: 'rgba(0, 0, 0, 1)',
                pointHoverBackgroundColor: 'rgba(0, 0, 0, 1)',
            },
            {
                label: 'Lele',
                data: [1, 1.5, 2.1, 2.3, 2.6, 3.1, 4, 4.2],
                borderWidth: 2,
                borderWidth: 2,
                backgroundColor: 'transparent',
                borderColor: 'rgba(63,82,227,.8)',
                pointBorderWidth: 0,
                pointRadius: 3.5,
                pointBackgroundColor: 'rgba(63,82,227,.8)',
                pointHoverBackgroundColor: 'rgba(63,82,227,.8)',
            },
            {
                label: 'Mas',
                data: [0.1, 0.4, 0.8, 1.2, 3, 4, 5, 5.5],
                borderWidth: 2,
                borderWidth: 2,
                backgroundColor: 'transparent',
                borderColor: 'rgba(229, 249, 9, 1)',
                pointBorderWidth: 0,
                pointRadius: 3.5,
                pointBackgroundColor: 'rgba(229, 249, 9, 1)',
                pointHoverBackgroundColor: 'rgba(229, 249, 9, 1)',
            },
            {
                label: 'Patin',
                data: [0, 0, 0, 0, 0, 0, 0, 0],
                borderWidth: 2,
                borderWidth: 2,
                backgroundColor: 'transparent',
                borderColor: 'rgba(25, 250, 10, 0.74)',
                pointBorderWidth: 0,
                pointRadius: 3.5,
                pointBackgroundColor: 'rgba(25, 250, 10, 0.74)',
                pointHoverBackgroundColor: 'rgba(25, 250, 10, 0.74)',
            },
        ]
    },
    options: {
        legend: {
            display: true
        },
        scales: {
            yAxes: [{
                gridLines: {
                    // display: false,
                    drawBorder: true,
                    color: '#f2f2f2',
                },
                ticks: {
                    beginAtZero: true,
                    stepSize: 1,
                    callback: function (value, index, values) {
                        return value + 'Kg';
                    }
                }
            }],
            xAxes: [{
                gridLines: {
                    display: false,
                    tickMarkLength: 15,
                }
            }]
        },
    }
});


$(document).ready(function () {
    // Setup - add a text input to each footer cell
    $('#mainTable tfoot th').each(function () {
        var title = $(this).text();
        $(this).html('<input type="text" placeholder="Search ' + title + '" />');
    });

    // DataTable
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