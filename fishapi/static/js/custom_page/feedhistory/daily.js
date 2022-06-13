/**
 *
 * You can write your JS code here, DO NOT touch the default style file
 * because it will make it harder for you to update.
 *
 */

"use strict";

$(document).ready(function () {
    $('#mainTable').DataTable();
    $('.tablesub').DataTable();
});

function setDate() {
    let date = document.getElementById("form-date").value;
    let link = document.getElementById("link-root").value;
    window.location.href = `${link}${date}`
}