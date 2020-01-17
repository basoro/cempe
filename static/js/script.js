function setCookie(name,value) {
var Days = 30;
var exp = new Date();
exp.setTime(exp.getTime() + Days*24*60*60*1000);
document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
}

function getCookie(name) {
	var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
	if(arr=document.cookie.match(reg))
		return unescape(arr[2]);
	else
		return null;
}

Date.prototype.format = function(format)
{
	 var o = {
	 "M+" : this.getMonth()+1, //month
	 "d+" : this.getDate(),    //day
	 "h+" : this.getHours(),   //hour
	 "m+" : this.getMinutes(), //minute
	 "s+" : this.getSeconds(), //second
	 "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
	 "S" : this.getMilliseconds() //millisecond
	 }
	 if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
	 (this.getFullYear()+"").substr(4 - RegExp.$1.length));
	 for(var k in o)if(new RegExp("("+ k +")").test(format))
	 format = format.replace(RegExp.$1,
	 RegExp.$1.length==1 ? o[k] :
	 ("00"+ o[k]).substr((""+ o[k]).length));
	 return format;
}

function getLocalTime(tm) {
	tm  = tm.toString();
	if(tm.length > 10){
		tm = tm.substring(0,10);
	}
	return new Date(parseInt(tm) * 1000).format("yyyy/MM/dd hh:mm:ss");
}

function ToSize(bytes){
	var unit = [' B',' KB',' MB',' GB'];
	var c = 1024;
	for(var i=0;i<unit.length;i++){
		if(bytes < c){
			return (i==0?bytes:bytes.toFixed(2)) + unit[i];
		}
		bytes /= c;
	}
}
