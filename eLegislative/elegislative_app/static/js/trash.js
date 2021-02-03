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
    let table =  $('#table_trash').DataTable({
        'columnDefs': [ {
            'targets': 0, /* column index */
            'orderable': false, /* true or false */
        }],
        // "drawCallback": function( settings ) {
        //     $("#table_trash thead").remove(); 
        // },
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
            table.rows().select(); 
        }else{
            $(".fa", this).removeClass("fa-check-square-o").addClass('fa-square-o');
            table.rows().deselect(); 
        } 
    });   
    $("#btn-trash-all").click(function(e){  
        let url = $(this).attr("data-url"); 
        let x = [];
        let container = [];
        var nodes = table.rows('.selected').nodes();  
        if(nodes.length > 0){
            for(let i = 0; i < nodes.length; i++){
                let tr = $(nodes[i]).children()[1];
                let dm = $(tr).attr("data-model");
                x.push(dm);
                
            }  

            var selectedRows = table.rows('.selected').data(); 
            for(let i = 0; i < selectedRows.length; i++){ 
                    selectedRows[i][0] = x[i]; 
                    let list = selectedRows[i];
                    container.push(list);
            }  

            let data = {
                'container':container
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
                    .html(`<p>Are your sure you want to delete this <b>${container.length}</b> records permanently?</p>`);
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
                <p>Please select the records you want to <b>delete</b> permanently!</p>
            </div>
            <div class="modal-footer">
            <button type="button" class="btn btn-outline pull-left" data-dismiss="modal">Close</button>
            </div>
            `);
            $("#modal-danger").modal("show");
            
        }
        
    });
    $("#modal-default").on("submit",".delete-records-permanently-form", function(e){
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
                    var rows = table
                    .rows( '.selected' )
                    .remove()
                    .draw();
                } 
            },
            complete: (data) => {

            },
            error: (data) => {
                $("#modal-default .modal-content")
                .html(data.html_form)
                .find(".modal-body")
                .html("Sorry this record has been already deleted, It is possible that you deleted it's parennt document before. please refresh the page.");


                $("#modal-default .modal-content")
                .html(data.html_form)
                .find(".modal-footer")
                .html(`<button type="button" class="btn btn-default pull-left" data-dismiss="modal">Close</button>`);

                var rows = table
                .rows( '.selected' )
                .remove()
                .draw();
            }

        });

        return false;

    });

    $("#btn-restore-all").click(function(e){
        let url = $(this).attr("data-url"); 
        let x = [];
        let container = [];
        var nodes = table.rows('.selected').nodes();  
        if(nodes.length > 0){
            for(let i = 0; i < nodes.length; i++){
                let tr = $(nodes[i]).children()[1];
                let dm = $(tr).attr("data-model");
                x.push(dm);
                
            }  

            var selectedRows = table.rows('.selected').data(); 
            for(let i = 0; i < selectedRows.length; i++){ 
                    selectedRows[i][0] = x[i]; 
                    let list = selectedRows[i];
                    container.push(list);
            }  

            let data = {
                'container':container
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
                    .html(`<p>Are your sure you want to restore this <b>${container.length}</b> records?</p>`);
                },
                complete: (data) => {

                },
                error: (data) => {

                }

            }); 
        }else{
            $("#modal-info .modal-content")
            .html(`
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title">No record selected</h4>
            </div>
            <div class="modal-body">
                <p>Please select the records you want to <b>restore</b>!</p>
            </div>
            <div class="modal-footer">
            <button type="button" class="btn btn-outline pull-left" data-dismiss="modal">Close</button>
            </div>
            `);
            $("#modal-info").modal("show");
            
        }
        
    });
    $("#modal-default").on("submit",".delete-records-permanently-form", function(e){
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
                    var rows = table
                    .rows( '.selected' )
                    .remove()
                    .draw();
                } 
            },
            complete: (data) => {

            },
            error: (data) => {
                $("#modal-default .modal-content")
                .html(data.html_form)
                .find(".modal-body")
                .html("Sorry this record has been already deleted, It is possible that you deleted it's parennt document before. please refresh the page.");


                $("#modal-default .modal-content")
                .html(data.html_form)
                .find(".modal-footer")
                .html(`<button type="button" class="btn btn-default pull-left" data-dismiss="modal">Close</button>`);

                var rows = table
                .rows( '.selected' )
                .remove()
                .draw();
            }

        });

        return false;

    });
    $("#modal-default").on("submit",".restore-records-form", function(e){
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
                    var rows = table
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
   // $(".checkbox-toggle").click(function () {
  //    var clicks = $(this).data('clicks');
  //    if (clicks) {
        //Uncheck all checkboxes
  //      $(".mailbox-messages input[type='checkbox']").iCheck("uncheck");
 //       $(".fa", this).removeClass("fa-check-square-o").addClass('fa-square-o');
 //     } else {
        //Check all checkboxes
  //      $(".mailbox-messages input[type='checkbox']").iCheck("check");
  //      $(".fa", this).removeClass("fa-square-o").addClass('fa-check-square-o');
  //    }
 //     $(this).data("clicks", !clicks);
  //  }); 
});