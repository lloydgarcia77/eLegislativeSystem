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
    $(".navbar-custom-menu .messages-menu .dropdown-menu .menu a").on("click",function(e){
        e.preventDefault();
        let url = $(this).attr('href');
        let data_url = $(this).attr('data-url'); 
        
        $.ajax({
            // https://docs.djangoproject.com/en/2.2/ref/csrf/
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            type: 'POST', // must be in POST
            url: data_url, 
            dataType: 'json',
            success: (data) => {
                if(data.status){
                    window.location.href = url;
                }
                
            },
            complete: (data) => {

            },
            error: (data) => {

            }

        }); 
        return false;
    }); 
    $(".navbar-custom-menu .messages-menu .dropdown-menu .footer a").on("click",function(e){ 
        let url = $(this).attr('data-url');   
        e.preventDefault();
         
         
        $.ajax({
            // https://docs.djangoproject.com/en/2.2/ref/csrf/
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            type: 'POST', // must be in POST
            url: url, 
            dataType: 'json',
            success: (data) => {
                if(data.status){
                    location.reload();
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