geogra_data = {};
$.ajax({
    type: "POST",
    url: "/geo/get/points/",
    data: {},
    async: false,
    dataType: "json",
    success: function (res) {//返回数据根据结果进行相应的处理
        geogra_data = res.points;
    },
    error: function () {
        alert("获取数据失败！");
    }
});

var min, max;
for (var points in geogra_data) {
    var data = geogra_data[points].value;
    if (points == 0) {
        max = data;
        min = data;
    } else {
        if (data - max > 0) {
            max = data;
        } else if (data - min < 0) {
            min = data;
        }
    }
}


var map = Loca.create('container', {
    mapStyle: 'amap://styles/26fc904bd43d8b834219809619ba4aea',
});

var layer = Loca.visualLayer({
        eventSupport: true,
        fitView: true,
        container: map,

        blendMode:'lighter',

        type: 'point',
        shape: 'circle',
        linewidth: 2,
        lineColor: '#fff',
    });

layer.on('mousemove', (ev) => {
    // 事件类型
    var type = ev.type;
    // 当前元素的原始数据
    var rawData = ev.rawData;
    // 原始鼠标事件
    var originalEvent = ev.originalEvent;
    openInfoWin(map.getMap(), originalEvent, {
        '位置': [rawData.latitude, rawData.longitude],
        '热度': rawData.value,
    });
});
layer.on('click', (ev) => {
    closeInfoWin();
});


layer.setData(geogra_data, {
    lnglat: function (data) {
        var item = data.value;
        return [item.longitude, item.latitude];
    }
});


layer.setOptions({
    style: {
        radius: function (data) {
            if (max === min)
                return 8;
            else
                return (data.value.value - min) / (max - min) * 8;
        },
        fill: function (data) {
            return '#cc589f';
        },
        opacity: 1,
    },
    // pointHoverStyle: {
    //     width: 10,
    //     height: 10,
    //     content: 'circle',
    //     fillStyle: 'rgba(0,0,0,0)',
    //     lineWidth: 2,
    //     strokeStyle: '#ffa500'
    // },
});
layer.render();


//文件上传部分
$.fn.csv2arr = function (callback) {
    console.log('你好');
    if (typeof(FileReader) == 'undefined') {    //if not H5
        alert("Your browser is too old,please use Chrome or Firefox");
        return false;
    }
    if (!$(this)[0].files[0]) {
        alert("Please select a file");
        return false;
    }
    var fReader = new FileReader();
    fReader.readAsDataURL($(this)[0].files[0]);
    $fileDOM = $(this);
    fReader.onload = function (evt) {
        var data = evt.target.result;
        var encoding = checkEncoding(data);
        Papa.parse($($fileDOM)[0].files[0], {
            encoding: encoding,
            complete: function (results) {
                var res = results.data;
                console.log("成功进入geo");
                $.ajax({
                    url: '/geo/points/upload/',
                    type: 'POST',
                    data: {json_data: JSON.stringify(res)},
                    dataType: 'html',
                    success: function (res) {
                        if (res == "true") {
                            alert('success !');
                            window.location.href = '/geo/points/';
                        } else {
                            alert('Unknown error.');
                        }
                    },
                    error: function () {
                        alert('Internet error');
                    }
                });
                if (res[res.length - 1] == "") {
                    res.pop();
                }
                callback && callback(res);
            }
        });
    };
    fReader.onerror = function (evt) {
        alert("The file has changed,please select again.(Firefox)");
    };

    function checkEncoding(base64Str) {
        var str = atob(base64Str.split(";base64,")[1]);
        var encoding = jschardet.detect(str);
        encoding = encoding.encoding;
        console.log(encoding);
        if (encoding == "windows-1252") {
            encoding = "ANSI";
        }
        return encoding;
    }
};

function read_file() {
    var file_name = $("input[name=csvfile]").val();
    if (file_name.lastIndexOf(".") != -1) {
        var fileType = (file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length)).toLowerCase();
        if (fileType == 'csv') {
            $("input[name=csvfile]").csv2arr(function (res) {
            });
        }
        else
            alert("Please use csv file")
    }
}

function uploadComplete(evt) {//py文件上传成功
    alert(evt.target.responseText);
}