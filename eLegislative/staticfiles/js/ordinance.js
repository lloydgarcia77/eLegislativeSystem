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
    let table =  $('#table_ordinance').DataTable({
        'columnDefs': [ {
            'targets': 3, /* column index */
            'orderable': false, /* true or false */
        }]
    }); 
    $("#table_ordinance").on("click", ".delete", function(e){
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
            success: (data) =>{
                $("#modal-default .modal-content").html(data.html_form);
            },
            complete: (data) => {

            },
            error: (data) => {

            }

        });
        
        return false;
    });
    $("#modal-default").on("submit",".delete-ordinance-form", function(e){
        e.preventDefault();
        let form = $(this);
        let row = $("#modal-default").data("tr");
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