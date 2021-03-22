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
    $("#btn-delete").click(function(e){
        let url = $(this).attr("data-url"); 
        let nodes = table_sent_items.rows(".selected").nodes();
        let id_list = [];
        if(nodes.length > 0){
            for(let index=0; index<nodes.length; index++){
                let tr = $(nodes[index]).children()[0];
                let id = $(tr).attr('data-id');
                id_list.push(id);
            }
            let data = {
                'id_list': id_list,
            }
            data = JSON.stringify(data);
            $.ajax({
                url: url,
                type: 'GET',
                dataType: 'json',
                beforeSend: () => {
                    $("#modal-default").data('data',data).modal("show");
                },
                success: (data) =>{
                    $("#modal-default .modal-content")
                    .html(data.html_form)
                    .find(".modal-body")
                    .html(`<p>Are your sure you want to delete this <b>${id_list.length}</b> messages permanently?</p>`);
                },
                complete: (data) => {

                },
                error: (data) => {

                }

            }); 
        }else{
            $("#modal-danger .modal-content")
            .html(`
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title">No record selected</h4>
            </div>
            <div class="modal-body">
                <p>Please select the messages you want to <b>delete</b> permanently!</p>
            </div>
            <div class="modal-footer">
            <button type="button" class="btn btn-outline pull-left" data-dismiss="modal">Close</button>
            </div>
            `);
            $("#modal-danger").modal("show");
        }
        
    }); 
    $("#modal-default").on("submit",".delete-sent-messages-permanently-form", function(e){
        e.preventDefault();
        let form = $(this);
        let data = $("#modal-default").data("data");
        let url = form.attr('data-url');  

        $.ajax({
            // https://docs.djangoproject.com/en/2.2/ref/csrf/
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            type: 'POST', // must be in POST
            url: url,
            data: data, // json object to be transfer
            dataType: 'json',
            success: (data) => {
                if(data.status){
                    $("#modal-default").modal("hide"); 
                    var rows = table_sent_items
                    .rows( '.selected' )
                    .remove()
                    .draw();
                } 
            },
            complete: (data) => {

            },
            error: (data) => {
                 
            }

        });

        return false;

    });
});