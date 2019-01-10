// 언어팩 선언.
$.lang = {};

$.lang.en = {
    "about": 'ABOUT',
    "contact": 'CONTACT',
    "home":"HOME",
    "product":"PRODUCT",
    "work":"WORK",
    "lab":"LAB",
    "market":"MARKET",
    "login":"LOGIN",
    "register":"REGISTER",

    "front-txt1":"DON'T JUST ANALYZE THE DATA - SHOW IT",
    "front-txt2":"A versatile platform for big data with cutting-edge technologies of data analytic and visualization.\n" +
        "Analyze the data with simple clicks",
    "front-txt3":"Start Gooing Now",
    "front-txt4":"Learn More",

    "login_txt1":"Login to your Account",
    "login_txt2":"Email:",
    "login_txt3":"Password:",
    "login_txt4":"Forgot Password?",
    "login_txt5":"Login",

    "signup_txt1":"Become a Gooer",
    "signup_txt2":"Email:",
    "signup_txt3":"Username:",
    "signup_txt4":"Password:",
    "signup_txt5":"Email Verification Code:",
    "signup_txt6":"By clicking the Register button, you agree to our <a href='/term1' target='_blank'>Terms of Service</a> and <a href='/term2' target='_blank'>Privacy Policy</a>.",
    "signup_txt7":"Register",
    "signup_txt8":"Get Code"
};

$.lang.cn = {
    "about": '关于我们',
    "contact": '联系我们',
    "home":"首页",
    "product":"产品",
    "work":"分析案例",
    "lab":"社区",
    "market":"市集",
    "login":"我的gooer",
    "register":"成为gooer",

    "front-txt1":"一键式数据分析平台",
    "front-txt2":"让每个人都能享受数据的乐趣",
    "front-txt3":"体验 dagoo",
    "front-txt4":"观看视频",

    "login_txt1":"登录账目",
    "login_txt2":"电子邮件:",
    "login_txt3":"密码:",
    "login_txt4":"忘记密码？",
    "login_txt5":"登录",

    "signup_txt1":"成为gooer",
    "signup_txt2":"电子邮件:",
    "signup_txt3":"用户名:",
    "signup_txt4":"密码:",
    "signup_txt5":"电子邮件验证码:",
    "signup_txt6":"点击注册按钮即表示您同意我们的 <a href='/term1' target='_blank'>服务条款</a>和<a href='/term2' target='_blank'>隐私政策</a>.",
    "signup_txt7":"注册",
    "signup_txt8":"获取代码"
};

/**
* setLanguage
* use $.lang[currentLanguage][languageNumber]
*/
function setLanguage(currentLanguage) {
    console.log("language: "+currentLanguage);
    $.cookie("lang",currentLanguage, { expires: 7, path: '/' });
  if(currentLanguage == "en"){
    $("#lang_select_img").attr("src","/static/new/theme/demos/seo/images/flags/usa.png");
    $("#lang_select_txt").text("En");
  }else if(currentLanguage == "cn"){
    $("#lang_select_img").attr("src","/static/new/theme/demos/seo/images/flags/chi.png");
    $("#lang_select_txt").text("Cn");
  }


  $('[data-langs]').each(function() {
    var $this = $(this);
    $this.html($.lang[currentLanguage][$this.data('langs')]);
  });
}

function init_lang(){
    console.log("init: "+$.cookie("lang"));
     if(!$.cookie("lang")){
         console.log("no language cookie");
        $.cookie("lang","en", { expires: 7, path: '/' });
    }

    let language= $.cookie("lang");

    if(language=="en"){
        setLanguage("en");
    }else if(language=="cn"){
        setLanguage("cn");
    }
}
$(document).ready(function() {
    init_lang();
});



