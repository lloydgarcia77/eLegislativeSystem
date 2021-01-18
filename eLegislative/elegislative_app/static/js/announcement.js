
$(document).ready(function () {
    let table =  $('#table_announcement').DataTable({
        'columnDefs': [ {
            'targets': 8, /* column index */
            'orderable': false, /* true or false */
        }]
    }); 
});