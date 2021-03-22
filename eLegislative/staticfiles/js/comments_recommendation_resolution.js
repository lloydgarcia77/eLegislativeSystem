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
    $("#input_comment").keypress(function(e){
        let key = e.which;
        if(key == 13){           
            let value = $("#input_comment").val();     
            if(value.trim() != ""){
                let url = $(this).attr("data-url"); 
                let data = {
                    "data": value,
                }; 
                data = JSON.stringify(data); 
                $.ajax({
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                    type: "POST",
                    url: url,
                    data: data,
                    dataType: 'json',
                    beforeSend: (data) =>{

                    },
                    success: (data) => { 
                        // Clearing the input box
                        $("#input_comment").val(""); 
                        $("#comment_section").append(
                            `
                            <div class="box-comment">
                                <img class="img-circle img-sm" src="${data["image"]}" alt="User Image"> 
                                <div class="comment-text">
                                    <span class="username">
                                    ${data["name"]}
                                        <span class="text-muted pull-right">${data["date_filed"]}
                                        <button class="btn btn-secondary btn-xs delete" data-url="${data['url']}"><i class="fa fa-trash"></i></button>
                                        </span>
                                    </span>
                                    ${data["message"]}
                                </div> 
                            </div>
                            `
                        ); 
                        $("#comment_count").text(`Total of: ${data["total"]} comments`)
                    },
                });
                
            }  
            
            return false;
        }
    });
    $("#comment_section").on("click",".delete", function(e){
        e.preventDefault(); 
        let row = $(this).closest('.box-comment');   
        let url = $(this).attr('data-url'); 
        $.ajax({
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            type: 'POST',
            url: url,
            dataType: 'json',
            success: (data) => {
                if(data.form_is_valid){
                    row.remove()
                    $("#comment_count").text(`Total of: ${data["total"]} comments`)
                }                
            }
        }) 
        return false;
    });
}); 