$(document).ready(function () {  
    // https://medium.com/typecode/a-strategy-for-handling-multiple-file-uploads-using-javascript-eb00a77e15f
    // https://stackoverflow.com/questions/57516816/cannot-add-csrf-token-to-xmlhttprequest-for-django-post-request
    // alert("asd"); 
    let dest_url = $("#btn-submit").attr("data-url"); 
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
    let fileInput = document.getElementById('file-input');
    let fileList = [];

    fileInput.addEventListener('change', function(e){
        fileList = [];
        // Clear table except the first row
        $("#table-files").find("tr:gt(0)").remove();

        for(let i =0; i <fileInput.files.length; i++){
            // Adding files to the list or array 
            fileList.push(fileInput.files[i]); 

            $("#table-files tbody").append(`<tr>
            <td >${i}.</td>
            <td>${fileInput.files[i]['name']}</td>
            <td>${fileInput.files[i]['size']}</td>
            <td>${fileInput.files[i]['lastModifiedDate']}</td>
            <td><button class="btn btn-danger btn-xs" data-id=${i}><i class="fa fa-trash btn-delete"></i></button></td>
             
            </tr>`);
        } 
        // Disable enable button if selected files or none
        if(fileInput.files.length > 0){
            $("#btn-submit").prop("disabled",false);
        }else{
            $("#btn-submit").prop("disabled",true);
        }
        $("#totalFiles").text(fileInput.files.length+" Files Selected"); 
   
    }); 

    
    // Sending the file to the server
    sendFile = function(file){
        let formData = new FormData();
        let request = new XMLHttpRequest();

        formData.set('file', file);  
        formData.append('data',JSON.stringify({"year":$("#year").val(),"remarks":$("#remarks").val()}));
        request.open("POST", dest_url);
        request.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        // request.setRequestHeader("Content-Type", "multipart/form-data"); 
        request.send(formData); 
    }

    // Iterating the list of files and send it parallel on the server
    let fileCatcher = document.getElementById('file-catcher'); 
    fileCatcher.addEventListener('submit', function(e){
        e.preventDefault();
        fileList.forEach(function(file){
            // sending the file on the server
            sendFile(file);
        });
    
        // Clearing the form after sending
        fileCatcher.reset();
        // Resetting the array
        fileList = [];
        $("#btn-submit").prop("disabled",true);
        $("#totalFiles").text(fileInput.files.length+" Files Selected");  
        // Clear table except the first row
        $("#table-files").find("tr:gt(0)").remove();
        $(".alert").show();
    }); 

    // Deleting selected row
    $("#table-files").on('click', '.btn-delete', function(e){
        e.preventDefault();
        $(this).closest('tr').remove();
        let id = $(this).closest('button').data('id'); 
        if(fileList.length > -1){
            // index to delete , # to delete
            fileList.splice(id,1);
        }
        return false;
    });
});