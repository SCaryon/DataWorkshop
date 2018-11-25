$.fn.csv2arr = function (callback) {
    if (typeof(FileReader) == 'undefined') {    //if not H5
        alert("Please use Chrome or Firefox");
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
                // console.log("被选中的是：", $("input[name=select]:checked").val());
                    $.ajax({
                        url: '/data_workshop',
                        type: 'POST',
                        data: {json_data: JSON.stringify(res)},
                        success: function (data) {
                            window.location.href = '/home'
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
        var file_name=$("input[name=csvfile]").val();
        if (file_name.lastIndexOf(".")!=-1){
            var fileType = (file_name.substring(file_name.lastIndexOf(".")+1,file_name.length)).toLowerCase();
            if(fileType=='csv')
            {
                $("input[name=csvfile]").csv2arr(function (res) {
                });
            }
        }
}