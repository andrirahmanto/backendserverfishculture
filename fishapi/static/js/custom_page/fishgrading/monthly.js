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
        datasets: [{
            label: 'Lele',
            data: [1, 1.5, 2.1, 2.3, 2.6, 3.1, 4, 4.2],
            borderWidth: 2,
            backgroundColor: 'rgba(63,82,227,.8)',
            borderWidth: 2,
            borderColor: 'rgba(63,82,227,.8)',
            pointBorderWidth: 0,
            pointRadius: 3.5,
            pointBackgroundColor: 'rgba(63,82,227,.8)',
            pointHoverBackgroundColor: 'rgba(63,82,227,.8)',
        },
        {
            label: 'Mas',
            data: [0.4, 1.1, 2, 2.1, 3.2, 3.4, 4, 4.3],
            borderWidth: 2,
            backgroundColor: 'rgba(254,86,83,.7)',
            borderWidth: 2,
            borderColor: 'rgba(254,86,83,.7)',
            pointBorderWidth: 0,
            pointRadius: 3.5,
            pointBackgroundColor: 'rgba(254,86,83,.7)',
            pointHoverBackgroundColor: 'rgba(254,86,83,.8)',
        }]
    },
    options: {
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                gridLines: {
                    // display: false,
                    drawBorder: false,
                    color: '#f2f2f2',
                },
                ticks: {
                    beginAtZero: true,
                    stepSize: 1500,
                    callback: function (value, index, values) {
                        return '$' + value;
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