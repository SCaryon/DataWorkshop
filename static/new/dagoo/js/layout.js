
if(window.location.pathname == "/new/"){


    $( window).scroll(function() {
       if($(window).scrollTop()<=25){
          $("#header-wrap").css("background-color","rgba(0,0,0,0)");
       }else{
           $("#header-wrap").css("background-color","#2d2d2d");
       }
    });
}

