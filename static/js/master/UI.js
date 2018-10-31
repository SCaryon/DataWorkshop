<!--比较外围的一些点击事件-->
function UI() {
    this.fullscreen = false;
    this.showabout = false;
    myThis = this;
    this.loading = 0;

    /*全屏事件处理*/
    //按键处理
    $(document).keyup(function (e) {
        switch (e.which) {
            case 37:
                break;
            case 27://press Esc then fullscreen=false
                THREEx.FullScreen.cancel();
                $("#fullscreen").html('<a href="#">全屏模式</a>');
                myThis.fullscreen = false;
                break;
            default:
                return;
        }
    });
    //在全屏的模式发生改变时触发
    $(window).bind('webkitfullscreenchange mozfullscreenchange fullscreenchange', function (e) {
        var state = document.fullScreen || document.mozFullScreen || document.webkitIsFullScreen;
        if (!state) {
            $("#fullscreen").html('<a href="#">全屏模式</a>');
            myThis.fullscreen = false;
            THREEx.FullScreen.cancel();
        }
    });

    //点击全屏时触发
    $("#fullscreen").click(function () {
        if (!myThis.fullscreen) {
            THREEx.FullScreen.request(document.body);
            $("#fullscreen").html('<a href="#">窗口模式</a>');
            myThis.fullscreen = true;
        } else {
            THREEx.FullScreen.cancel();
            $("#fullscreen").html('<a href="#">全屏模式</a>');
            myThis.fullscreen = false;
        }
    });

    //展示/隐藏about
    $("#showAbout").click(function () {
        myThis.showabout = !myThis.showabout;
        if (myThis.showabout) {
            $("#aboutText").show();
            $("#aboutText").animate({'right': '0'}, 400, "swing", function () {

            });
        } else {
            $("#aboutText").animate({'right': -window.innerWidth * 0.4 + 'px'}, 200, "swing", function () {
                $("#aboutText").hide();
            });
        }
    });
    $("#closeAbout").click(function () {
        myThis.showabout = false;
        $("#aboutText").animate({'right': -window.innerWidth * 0.4 + 'px'}, 200, "swing", function () {
            $("#aboutText").hide();
        });
    });


    /*下面是左边的选择展示模式的按钮的添加*/
    ring = true;
    buttons = [];
    divX = 45;
    divY = 60;
    step = 30;
    ring = false;
    buttons.push({
        "id": "gridSphereButton",
        "title": "全球视图",
        "img": "images/master/icon/globe2.png",
        "desc": "以3D球的形式,通过将出口额以点的形式放置在国家内来展示一个国家的出口量"
    });
    buttons.push({
        "id": "gridButton",
        "title": "地图视图",
        "img": "images/master/icon/map2.png",
        "desc": "以2D平面的形式,通过将出口额以点的形式放置在国家内来展示一个国家的出口量"
    });
    buttons.push({
        "id": "towersButton",
        "title": "堆积视图",
        "img": "images/master/icon/stacks32.png",
        "desc": "将一个国家的产品出口量堆叠在地图中来展示该国家的出口量,每行表示 $2.5B"
    });
    buttons.push({
        "id": "productButton3",
        "title": "3D产品空间",
        "img": "images/master/icon/graph2.png",
        "desc": "产品空间的3D版本,通过单击节点来跳转"
    });
    buttons.push({
        "id": "productButton",
        "title": "产品空间",
        "img": "images/master/icon/graph22.png",
        "desc": "显示其类别中的所有产品，排列在称为产品空间的相似性图表中。"
    });
    buttons.push({
        "id": "productButton2",
        "title": "产品堆积",
        "img": "images/master/icon/stack2.png",
        "desc": "按类别堆叠产品"
    });
    buttons.push({
        "id": "groupButton",
        "title": "分类展示",
        "img": "images/master/icon/stack.png",
        "desc": "按照产品类别将产品的分布分别展示"
    });
    // buttons.push({
    //     "id": "anchorButton",
    //     "title": "cities",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });
    // buttons.push({
    //     "id": "blendButton",
    //     "title": "blend",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });
    // buttons.push({
    //     "id": "centerButton",
    //     "title": "center",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });
    // buttons.push({
    //     "id": "piesButton",
    //     "title": "pies",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });
    // buttons.push({
    //     "id": "globeProbaButton",
    //     "title": "probability3D",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });
    // buttons.push({
    //     "id": "probaButton",
    //     "title": "probability",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });
    //
    // buttons.push({
    //     "id": "globeButton",
    //     "title": "globe",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });
    // buttons.push({
    //     "id": "histButton",
    //     "title": "histogram",
    //     "img": "images/master/icon/stack2.png",
    //     "desc": "按类别堆叠产品"
    // });


    newDiv = "<table>";
    for (var i = 0; i < buttons.length; i++) {
        option = buttons[i];
        option.rank = i;
        angle = 0;
        if (i % 2 == 0 && i > 0) {
            newDiv += "</tr><tr>";
        }
        newDiv += "<td>" +
            "<div class='modeSelector' style='-webkit-transform: rotateY(" + angle + "deg);" +
            "transform: rotateY(" + angle + "deg);'id='" + option.id + "'>" +
            "<img style='max-width:58px;margin: 0 auto;' src='/static/" + option.img + "'/>" +
            "<div class='optionTitle'>" + option.title + "</div></div></td>";
    }
    newDiv += "</tr></table>";

    $("#visualizations").html(newDiv);
    $("#gridSphereButton").addClass("selectedMode");
    $("#visualizations").on("mouseover", ".modeSelector", function () {
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].id === $(this).prop('id')) {
                $("#modeDescription").show();
                $("#modeDescription").html(buttons[i].desc);
                offset = $(this).offset();
                $("#modeDescription").css({'top': offset.top, 'left': '140px','z-index':'100'});
            }
        }
    });
    $("#visualizations").on("mouseout", ".modeSelector", function () {
        $("#modeDescription").hide();
    });

};

//增加加载时动画
UI.prototype.addSpinner = function () {
    var opts = {
        lines: 17 // The number of lines to draw
        , length: 0 // The length of each line
        , width: 1 // The line thickness
        , radius: 84 // The radius of the inner circle
        , scale: 3.5 // Scales overall size of the spinner
        , corners: 1 // Corner roundness (0..1)
        , color: '#FFF' // #rgb or #rrggbb or array of colors
        , opacity: 0 // Opacity of the lines
        , rotate: 0 // The rotation offset
        , direction: 1 // 1: clockwise, -1: counterclockwise
        , speed: 1 // Rounds per second
        , trail: 99 // Afterglow percentage
        , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
        , zIndex: 2e9 // The z-index (defaults to 2000000000)
        , className: 'spinner' // The CSS class to assign to the spinner
        , top: '50%' // Top position relative to parent
        , left: '50%' // Left position relative to parent
        , shadow: false // Whether to render a shadow
        , hwaccel: false // Whether to use hardware acceleration
        , position: 'absolute' // Element positioning
    };
    var target = document.getElementById('spinner');
    var spinner = new Spinner(opts).spin(target);

};
//建立最下方的目录
UI.prototype.buildCategories = function (categories) {
    cats = ["动物和动物产品","蔬菜产品","食品","矿物产品","化学品联合工业","塑料和橡胶","皮革和毛皮","木材和木制品","纺织品" ,"鞋类和头饰","石材和玻璃","金属","机电","运输","其他","服务"];    var catHTML = "<table><tr>";
    $.each(categories, function (i, val) {
        color = new THREE.Color(i);
        rgba = "rgba(" + Math.round(color.r * 295) + "," + Math.round(color.g * 295) + "," + Math.round(color.b * 295) + ",0.8)";
        catHTML += "<td class='categoryButton' style='border-top:8px solid " + rgba + " ;'><div id=cat" + val.id + " class='chooseCategory'>" + cats[val.id] + " </div></td>";
    });
    $("#categories").html(catHTML + "</tr></table>");
};
//加载中的时候展示加载速度
UI.prototype.updateLoader = function (add) {
    this.loading += add;
    percentage = this.loading;
    $("#loadingBar").animate({'width': percentage / 100 * 500}, 100);
};

//嵌入产品选择框
UI.prototype.createProductBox = function (products) {
    var html = '<select class="productSelection"><option value="null" selected="selected">选择产品</option>';

    $.each(products, function (i, val) {
        html += "<option value ='" + val.atlasid + "'>" + val.name + "</option>";
    });
    html += "</select>";
    $(".productBox").html(html);
    $(".productSelection").select2({placeholder: "product", allowClear: true});

};

//改变鼠标箭头样式
UI.prototype.changeCursor = function (type, blocked) {
    $('body').removeClass("grab");
    $('body').removeClass("grabbing");
    switch (type) {
        case "grab":
            if (blocked) $('body').css({"cursor": "not-allowed"});
            else $('body').addClass("grab");
            break;
        case "grabbing":
            if (blocked) $('body').css({"cursor": "not-allowed"});
            else $('body').addClass("grabbing");
            break;
        case "default":
        case "pointer":
        default:
            $('body').css({"cursor": type});
            break;
    }

};
//创建国家选择框
UI.prototype.createSelectionBox = function (countries) {
    var html = '<select class="countrySelection"><option value="null" selected="selected">选择国家</option>';

    $.each(countries, function (i, val) {
        html += "<option value ='" + i + "'>" + val.name + "</option>";
    });
    html += "</select>";
    $(".selectionBox").html(html);
    $(".countrySelection").select2({placeholder: "country", allowClear: true});

};