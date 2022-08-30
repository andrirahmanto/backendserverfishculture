/**
 *
 * You can write your JS code here, DO NOT touch the default style file
 * because it will make it harder for you to update.
 *
 */

"use strict";
var month = ["January", "February", "March", "April", "May", "June", "July", "August"];
var nilaMerahData = [];
var nilaHitamData = [];
var leleData = [];
var masData = [];
var patinData = [];

async function getGradingData() {
    var apiUrl = document.getElementById("link-graph").value;

    const response = await fetch(apiUrl)
    const gradingData = await response.json()
    console.log(gradingData)

    nilaMerahData = gradingData["nila merah"];
    nilaHitamData = gradingData["nila hitam"];
    leleData = gradingData["lele"];
    masData = gradingData["mas"];
    patinData = gradingData["patin"];
}

async function gradingChart() {
    await getGradingData();

    var ctx = document.getElementById("myChart").getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: month,
            datasets: [
                {
                    label: 'Nila Merah',
                    data: nilaMerahData,
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
                    data: nilaHitamData,
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
                    data: leleData,
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
                    data: masData,
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
                    data: patinData,
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
}

var ctx = document.getElementById("myChart").getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: month,
        datasets: [
            {
                label: 'Nila Merah',
                data: nilaMerahData,
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
                data: nilaHitamData,
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
                data: leleData,
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
                data: masData,
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
                data: patinData,
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
    gradingChart()
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