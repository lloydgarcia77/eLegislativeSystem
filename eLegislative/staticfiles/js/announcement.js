
$(document).ready(function () { 
    let table =  $('#table_announcement').DataTable({
        'columnDefs': [ {
            'targets': 7, /* column index */
            'orderable': false, /* true or false */
        }]
    });  
    $("#create-announcement").on("click", function(e){
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

            },
            complete: (data) => {

            },
            error: (data) => {

            }
        });
        return false;
    });

    $("#modal-default").on("submit", ".create-announcement-form", function(e){
        e.preventDefault();
        let form =$(this);

        $.ajax({
            url: form.attr("data-url"),
            data: form.serialize(),
            cache: false,
            type: form.attr("method"),
            dataType: 'json',
            beforeSend: () => {
                $("#modal-default").modal("show");
            },
            success: (data) => {
                if(data.form_is_valid){
                    let a_response = data.a_response;
                    let visible = a_response['visible'] ? `<td><span class="label label-success">${a_response['visible']}</span></td>` : `<td><span class="label label-danger">${a_response['visible']}</span></td>` ;                    
                    table.row.add([
                        `<td>${a_response['aid']}</td>`,
                        `<td>${a_response['title']}</td>`,
                        `<td>${a_response['subject']}</td>`,
                        `<td>${a_response['content']}</td>`,
                        visible,
                        `<td>${a_response['author']}</td>`,
                        `<td>${a_response['date_filed']}</td>`,
                        `
                        <div class="btn-group">
                            <button type="button" class="btn btn-default btn-flat">Action</button>
                            <button type="button" class="btn btn-default btn-flat dropdown-toggle" data-toggle="dropdown" aria-expanded="true">
                                <span class="caret"></span>
                                <span class="sr-only">Toggle Dropdown</span>
                            </button>
                            <ul class="dropdown-menu" role="menu">
                                <li><a href="${a_response['edit_url']}" class="edit">Edit</a></li>
                                <li><a href="${a_response['delete_url']}" class="delete">Delete</a></li>              
                            </ul>
                        </div>
                        `
                    ]).draw(false);

                    $("#modal-default").modal("hide");
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
 
    $("#table_announcement").on("click", ".delete", function(e){
        e.preventDefault();
        let url = $(this).attr("href");
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
            },
            complete: (data) => {

            },
            error: (data) => {

            }
        });
        return false;
    });

    $("#modal-default").on("submit", ".delete-announcement-form", function(e){
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

    $("#table_announcement").on('click', ".edit", function(e){
        e.preventDefault();
        let url = $(this).attr("href");
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
            },
            complete: (data) => {

            },
            error: (data) => {

            }
        }); 

        return false;
    });

    $("#modal-default").on("submit", ".edit-announcement-form", function(e){
        e.preventDefault();
        let form =$(this);
        let row = $("#modal-default").data('tr'); 

        $.ajax({
            url: form.attr("data-url"),
            data: form.serialize(),
            cache: false,
            type: form.attr("method"),
            dataType: 'json',
            beforeSend: () => {
                $("#modal-default").modal("show");
            }, 
            success: (data) => {
                if(data.form_is_valid){
                    let a_response = data.a_response;
                    let visible = a_response['visible'] ? `<td><span class="label label-success">${a_response['visible']}</span></td>` : `<td><span class="label label-danger">${a_response['visible']}</span></td>` ;                    
                    let row_data = table.row(row).data();
                    row_data[1] = `<td>${a_response['title']}</td>`;
                    row_data[2] = `<td>${a_response['subject']}</td>`;
                    row_data[3] = `<td>${a_response['content']}</td>`;
                    row_data[4] = visible;
                    row_data[5] = `<td>${a_response['author']}</td>`;
                    //https://legacy.datatables.net/ref
                    $('#table_announcement').dataTable().fnUpdate(row_data,row,undefined,false); 
                    $("#modal-default").modal("hide");
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
 


});