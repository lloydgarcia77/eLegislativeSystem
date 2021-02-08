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
    let table_sent_items =  $('#table_sent_messges').DataTable({ 
        'columnDefs': [ {
            'targets': 0, /* column index */
            'orderable': false, /* true or false */
            
        }], 
        "drawCallback": function( settings ) {
            $("#table_sent_messges thead").remove(); 
        },
 
        select: {
            style:    'os',
            selector: 'td:first-child'
        },
        order: [[ 1, 'asc' ]] 
    });  
    $("#btn-select-all").click(function(e){
        //https://jsfiddle.net/annoyingmouse/yxLrLr8o/
        //https://datatables.net/extensions/select/examples/initialisation/checkbox.html
        //https://datatables.net/forums/discussion/44089/is-it-possible-to-hide-the-row-with-column-headers
        
        let click =  $(this).data('clicks') ? $(this).data('clicks',false) : $(this).data('clicks',true);
        if(click.data('clicks')){
            $(".fa", this).removeClass("fa-square-o").addClass('fa-check-square-o');
            table_sent_items.rows().select(); 
        }else{
            $(".fa", this).removeClass("fa-check-square-o").addClass('fa-square-o');
            table_sent_items.rows().deselect(); 
        } 
    });    
   

});