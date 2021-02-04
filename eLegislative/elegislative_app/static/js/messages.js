$(document).ready(function () {
    function getCookie(cname) {
        var name = cname + "=";
        var decodedCookie = decodeURIComponent(document.cookie);
        var ca = decodedCookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    } 
    let table_inbox =  $('#table_inbox').DataTable({ 
        'columnDefs': [ {
            'targets': 0, /* column index */
            'orderable': false, /* true or false */
            
        }], 
        "drawCallback": function( settings ) {
            $("#table_inbox thead").remove(); 
        },
 
        select: {
            style:    'os',
            selector: 'td:first-child'
        },
        order: [[ 1, 'asc' ]] 
    }); 
});