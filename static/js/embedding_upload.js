    $.fn.embedding_csv2arr = function (callback) {
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
        console.log($(this)[0].files[0]);
        $fileDOM = $(this);
        fReader.onload = function (evt) {
            var data = evt.target.result;
            var encoding = checkEncoding(data);
            Papa.parse($($fileDOM)[0].files[0], {
                encoding: encoding,
                complete: function (results) {
                    var res = results.data;
                    $.ajax({
                        url: '/data_workshop',
                        type: 'POST',
                        data: {json_data: JSON.stringify(res)},
                        dataType: 'html',
                        success:function(){
                            alert('upload the data file successfully !');
                            a = document.createElement('a');
                            a.href = '/embedding';
                            a.click();
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
                encoding.detecting = "ANSI";
            }
            return encoding;
        }
    };
$.fn.cluster_csv = function (callback) {
    alert("hello!")
}
function read_embedding_file(){
    var file_name=$("input[name=cluster_csvfile]").val();
    if (file_name.lastIndexOf(".")!=-1){
var fileType = (file_name.substring(file_name.lastIndexOf(".")+1,file_name.length)).toLowerCase();
if(fileType=='csv')
{
    $("input[name=cluster_csvfile]").embedding_csv2arr(function(res){
    });
}
if(fileType=='py')
{
var fd=new FormData();

fd.append("file",document.getElementById('embedding_csvfile').files[0]);//这是获取上传的文件
fd.append('label','py');
    var xhr=new XMLHttpRequest();
    xhr.open("POST","/User_code");//要传到后台方法的路径
    xhr.addEventListener("load",uploadComplete,false);
xhr.send(fd)
    };
if(fileType=='so')
{
var fd=new FormData();

fd.append("file",document.getElementById('embedding_csvfile').files[0]);//这是获取上传的文件
fd.append('label','so');
    var xhr=new XMLHttpRequest();
    xhr.open("POST","/User_code");//要传到后台方法的路径
    xhr.addEventListener("load",uploadComplete,false);
xhr.send(fd)
    };
if(fileType=='jar')
{
var fd=new FormData();

fd.append("file",document.getElementById('embedding_csvfile').files[0]);//这是获取上传的文件
fd.append('label','jar');
    var xhr=new XMLHttpRequest();
    xhr.open("POST","/User_code");//要传到后台方法的路径
    xhr.addEventListener("load",uploadComplete,false);
xhr.send(fd)
    };
if(fileType=='zip')
{
var fd=new FormData();

fd.append("file",document.getElementById('embedding_csvfile').files[0]);//这是获取上传的文件
    fd.append('label','zip');

    var xhr=new XMLHttpRequest();
    xhr.open("POST","/User_code");//要传到后台方法的路径
    xhr.addEventListener("load",uploadComplete,false);
xhr.send(fd);
};
}
    }



function uploadComplete(evt){//py文件上传成功
alert(evt.target.responseText);
}