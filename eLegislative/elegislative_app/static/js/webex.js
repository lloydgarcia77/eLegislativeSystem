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
                    // let concern_date_dict = data.concern_date_dict;
                    // let id  = concern_date_dict["id"];
                    // let subject  = concern_date_dict["subject"];
                    // let date_filed  = concern_date_dict["date_filed"];
                    // let edit_url  = concern_date_dict["edit_url"];
                    // let delete_url  = concern_date_dict["delete_url"];
                    // let view_url  = concern_date_dict["view_url"];
                    // let myJSON = JSON.stringify(concern_date_dict,undefined, 4); 
                    $("#modal-default").modal('hide');
                    // table.row.add([
                    //     `<span class="badge bg-red">${id}</span> `,
                    //     `<span class="label label-info">${subject}</span>`,
                    //     `<span class="label label-default">${date_filed}</span> `,
                    //     `
                    //     <div class="text-center"> 
                    //     <div class="btn-group">
                    //     <button type="button" class="btn btn-danger btn-delete" data-toggle="tooltip" title="Delete" data-url="${delete_url}"><i class="fa fa-fw fa-trash"></i></button>                    
                    //     <button type="button" class="btn btn-warning btn-view" data-toggle="tooltip" title="View" data-url="${view_url}"><i class="fa fa-fw fa-eye"></i></button>
                    //     <button type="button" class="btn btn-info btn-edit" data-toggle="tooltip" title="Edit" data-url="${edit_url}"><i class="fa fa-fw fa-pencil-square-o"></i></button>
                    //     </div>
                    //     </div>
                    //     `
                    // ]).draw(false);
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