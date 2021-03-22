$(document).ready(function () {
    let table =  $('#table_webex').DataTable({
        'columnDefs': [ {
            'targets': 7, /* column index */
            'orderable': false, /* true or false */
        }]
    }); 

    $("#addWebExLinks").on('click', function(e){
        e.preventDefault();
        let url = $(this).attr("href");
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            beforeSend: () => {
                $("#modal-default").modal("show"); 
                
            },
            success: (data) => {
                $("#modal-default .modal-content").html(data.html_form);
                $('#modal-default .select2').select2();
            },
            complete: (data) => {

            },
            error: (data) => {

            }
        });
        return false;
    });

    $("#modal-default").on("submit", ".add-webex-link", function(e){
        e.preventDefault();
        let form = $(this);

        $.ajax({
            url:  form.attr("data-url"),
            data: form.serialize(),
            cache: false,
            type: form.attr("method"),
            dataType: 'json',
            beforeSend: () => {
                $("#modal-default").modal("show"); 
                $('#modal-default .select2').select2();
            },
            success: (data) => {
                if(data.form_is_valid){
                    let webex = data.webex;
                    let id  = webex["id"];
                    let url  = webex["url"];
                    let display_text  = webex["display_text"];
                    let protocol  = webex["protocol"];
                    let remarks  = webex["remarks"];
                    let author  = webex["author"];
                    let date_filed  = webex["date_filed"];
                    let eurl  = webex["eurl"];
                    let durl  = webex["durl"];
                    let json_webex = JSON.stringify(webex,undefined, 4); 
                 
                    $("#modal-default").modal('hide');
                    table.row.add([
                        `${id}`,
                        `<a href="${url}" target="_blank">${url}</a>`,
                        `${display_text}`,
                        `${protocol}`,
                        `${remarks}`,
                        `${author}`,
                        `${date_filed}`, 
                        `
                        <div class="text-center"> 
                        <div class="btn-group">
                        <button type="button" class="btn btn-warning btn-flat btn-edit" data-toggle="tooltip" title="Edit" data-url="${eurl}"><i class="fa fa-edit"></i></button>
                        <button type="button" class="btn btn-danger btn-flat btn-delete" data-toggle="tooltip" title="Delete" data-url="${durl}"><i class="fa fa-trash"></i></button>                                                
                         </div>
                        </div>
                        `
                    ]).draw(false);
                }else{
                    $("#modal-default .modal-content").html(data.html_form);
                }

            },
            complete: (data) => {

            },
            error: (data) => {

            }
        });
        return false;
    });
 
    $("#table_webex").on('click', ".btn-edit", function(e){
        e.preventDefault();
        let url = $(this).attr("data-url");
        let row = $(this).closest('tr');  
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            beforeSend: () => { 
                $("#modal-default").data('tr',row).modal("show");
            },
            success: (data) => {
                $("#modal-default .modal-content").html(data.html_form);
                $('#modal-default .select2').select2();
            },
            complete: (data) => {

            },
            error: (data) => {

            }
        }); 

        return false;
    });

    $("#modal-default").on("submit",".edit-webex-link", function(e){
        e.preventDefault();
        let form = $(this); 
        let row = $("#modal-default").data('tr'); 

        $.ajax({
            url: form.attr("data-url"),
            data: form.serialize(),
            cache: false,
            type: form.attr("method"),
            dataType: 'json',
            success: (data) => {
                if(data.form_is_valid){  
                    let webex = data.webex; 
                    let url  = webex["url"];
                    let display_text  = webex["display_text"];
                    let protocol  = webex["protocol"];
                    let remarks  = webex["remarks"];
                    let author  = webex["author"];
           
                    $("#modal-default").modal("hide");
                    let row_data = table.row(row).data();
                    row_data[1] = `<a href="${url}" target="_blank">${url}</a>`;
                    row_data[2] = `${display_text}`;
                    row_data[3] = `${protocol}`;
                    row_data[4] = `${remarks}`;
                    row_data[5] = `${author}`;

                    //https://legacy.datatables.net/ref
                    $('#table_webex').dataTable().fnUpdate(row_data,row,undefined,false); 
                }else{
                    $("#modal-form .modal-content").html(data.html_form);
                }
            }
        });

        return false;
    });
    $("#table_webex").on('click', ".btn-delete", function(e){
        e.preventDefault(); 
        let url = $(this).attr("data-url");
        let row = $(this).closest('tr'); 
        //table.row(row).remove().draw(); 
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            beforeSend: () => {
                //$("#modal-default").modal("show");
                $("#modal-default").data('tr',row).modal("show");
            },
            success: (data) => {
                $("#modal-default .modal-content").html(data.html_form);
            },
            complete: (data) => {

            },
            error: (data) => {

            }
        });

        return false;
    });
    $("#modal-default").on("submit",".delete-webex-link", function(e){
        e.preventDefault();
        let form = $(this); 
        let row = $("#modal-default").data('tr');
        
        $.ajax({
            url: form.attr("data-url"),
            data: form.serialize(),
            cache: false,
            type: form.attr("method"),
            dataType: 'json',
            success: (data) => {
                if(data.form_is_valid){  
                    $("#modal-default").modal("hide");
                    table.row(row).remove().draw();    
                }else{
                    $("#modal-form .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    });

});