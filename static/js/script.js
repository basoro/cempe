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

function openPath(path){
	setCookie('Path',path);
	window.location.href = '/files';
}

function OnlineEditFile(type, fileName) {
	if (type != 0) {
		var path = $("#PathPlace input").val();
		var data = encodeURIComponent($("#textBody").val());
		var encoding = $("select[name=encoding]").val();
		layer.msg('Saving...', {
			icon: 16,
			time: 0
		});
		$.post('/files?action=SaveFileBody', 'data=' + data + '&path=' + fileName+'&encoding='+encoding, function(rdata) {
			if(type == 1) layer.closeAll();
			layer.msg(rdata.msg, {
				icon: rdata.status ? 1 : 2
			});
		});
		return;
	}

	var loadT = layer.msg('Reading file...', {
		icon: 16,
		time: 0
	});
	var exts = fileName.split('.');
	var ext = exts[exts.length-1];
	var msg = 'Online editing only supports text and script files, default UTF8 encoding, do you try to open it? ';
	if(ext == 'conf' || ext == 'cnf' || ext == 'ini'){
		msg = 'What you are opening is a configuration file. If you don\'t understand the configuration rules, the configuration program may not work properly. Continue? ';
	}
	var doctype;
	switch (ext){
		case 'html':
			var mixedMode = {
				name: "htmlmixed",
				scriptTypes: [{matches: /\/x-handlebars-template|\/x-mustache/i,
							   mode: null},
							  {matches: /(text|application)\/(x-)?vb(a|script)/i,
							   mode: "vbscript"}]
			  };
			doctype = mixedMode;
			break;
		case 'htm':
			var mixedMode = {
				name: "htmlmixed",
				scriptTypes: [{matches: /\/x-handlebars-template|\/x-mustache/i,
							   mode: null},
							  {matches: /(text|application)\/(x-)?vb(a|script)/i,
							   mode: "vbscript"}]
			  };
			doctype = mixedMode;
			break;
		case 'js':
			doctype = "text/javascript";
			break;
		case 'json':
			doctype = "application/ld+json";
			break;
		case 'css':
			doctype = "text/css";
			break;
		case 'php':
			doctype = "application/x-httpd-php";
			break;
		case 'tpl':
			doctype = "application/x-httpd-php";
			break;
		case 'xml':
			doctype = "application/xml";
			break;
		case 'sql':
			doctype = "text/x-sql";
			break;
		case 'conf':
			doctype = "text/x-nginx-conf";
			break;
		default:
			var mixedMode = {
				name: "htmlmixed",
				scriptTypes: [{matches: /\/x-handlebars-template|\/x-mustache/i,
							   mode: null},
							  {matches: /(text|application)\/(x-)?vb(a|script)/i,
							   mode: "vbscript"}]
			  };
			doctype = mixedMode;
	}
	$.post('/files?action=GetFileBody', 'path=' + fileName, function(rdata) {
		layer.close(loadT);
		var val = ''
		var editorbox = layer.open({
			type: 1,
			shift: 5,
			closeBtn: 2,
			area: ['90%', '90%'],
			title: 'Online editing [' + fileName + ']',
			content: '<form class="zun-form-new" style="padding-top:10px">\
			<div class="line noborder">\
			<textarea class="mCustomScrollbar" id="textBody" style="width:100%;margin:0 auto;line-height: 1.8;position: relative;top: 10px;" value="" />\
			</div>\
			<div class="submit-btn" style="position:absolute; bottom:0; width:100%">\
			<button type="button" class="btn btn-danger btn-sm btn-title btn-editor-close">Close</button>\
			<button id="OnlineEditFileBtn" type="button" class="btn btn-info btn-sm btn-title">Save</button>\
			</div>\
			</form>'
		});
		$("#textBody").text(rdata.data);
		//$(".layui-layer").css("top", "5%");
		var h = $(window).height()*0.9;
		$("#textBody").height(h-120);
		var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
			extraKeys: {"Ctrl-F": "findPersistent","Ctrl-H":"replaceAll","Ctrl-S":function(){
					$("#textBody").text(editor.getValue());
					OnlineEditFile(2,fileName);
				}
			},
			mode:doctype,
			lineNumbers: true,
			matchBrackets:true,
			matchtags:true,
			autoMatchParens: true
		});
		editor.focus();
		editor.setSize('auto',h-110);
		$("#OnlineEditFileBtn").click(function(){
			$("#textBody").text(editor.getValue());
			OnlineEditFile(1,fileName);
		});
		$(".btn-editor-close").click(function(){
			layer.close(editorbox);
		})
	});
}

function ServiceAdmin(name,type){
	var data = "name="+name+"&type="+type;
	var msg = '';
	switch(type){
		case 'stop':
			msg = 'stop';
			break;
		case 'start':
			msg = 'start';
			break;
		case 'restart':
			msg = 'restart';
			break;
		case 'reload':
			msg = 'reload';
			break;
	}
	layer.confirm('Do you really want to '+msg+' '+name+' service? ',{closeBtn:2},function(){
		var loadT = layer.msg('Being '+msg+' '+name+' service...',{icon:16,time:0});
		$.post('/system?action=ServiceAdmin',data,function(rdata){
			layer.close(loadT);
			var reMsg =rdata.status?name+' service has success '+msg:name+' service '+msg+'! ';
			layer.msg(reMsg,{icon:rdata.status?1:2});

			if(type != 'reload' && rdata.status == true){
				setTimeout(function(){
					window.location.reload();
				},1000)
			}
			if(!rdata.status) layer.msg(rdata.msg,{icon:2,time:0,shade:0.3,shadeClose:true});

		}).error(function(){
			layer.close(loadT);
			layer.msg('Successful operation!',{icon:1});
		});
	});
}

function GetConfigFile(type){
	var fileName = '';
	switch(type){
		case 'mysql':
			fileName = '/etc/my.cnf';
			break;
		case 'nginx':
			fileName = '/etc/nginx/nginx.conf';
			break;
		case 'php-fpm':
			fileName = '/etc/php.ini';
			break;
		default:
			fileName = '/etc/php.ini';
			break;
	}

	OnlineEditFile(0,fileName);
}

function SafeMessage(title,msg,success,thtml){
	if(thtml == undefined) thtml = "";
	layer.open({
		type: 1,
	    title: title,
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='zun-form-new webDelete'>\
	    	<p>" + msg + "</p>\
	    	" + thtml + "\
	    	<div class='submit-btn' style='margin-top:15px'>\
				<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>Cancel</button>\
		        <button type='button' id='toSubmit' class='btn btn-info btn-sm btn-title' >Submit</button>\
	        </div>\
	    </div>"
	});


	$("#toSubmit").click(function(){
		success();
	});
}
