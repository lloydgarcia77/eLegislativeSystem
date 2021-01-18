$(document).ready(function () {

    let table_committee_report_ordinance =  $('#table_committee_report_ordinance').DataTable({
        'columnDefs': [ {
            'targets': 8, /* column index */
            'orderable': false, /* true or false */
        }]
    }); 

});