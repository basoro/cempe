function getData(page,search) {
	search = search == undefined ? '':search;
	var sUrl = '/data?action=getData';
	var sUrlData='tojs=getData&table=databases&limit=15&p='+page+'&search='+search;
	var loadT = layer.load();
	$.post(sUrl, sUrlData,function(data) {
		layer.close(loadT);
		var Body = '';
		if(data.data == ""){
			Body="<tr><td colspan='7'>There is currently no database data</td></tr>";
			$("#DataPage").hide()
		}
		else{
			$("#DataPage").show();
			for (var i = 0; i < data.data.length; i++) {
				if(data.data[i].backup_count==0){
					var isback = "<a href='javascript:;' class='link' onclick=\"DataDetails('"+data.data[i].id+"','"+data.data[i].name+"')\">No packaging</a>"
				}else{
					var isback = "<a href='javascript:;' class='link' onclick=\"DataDetails('"+data.data[i].id+"','"+data.data[i].name+"')\">Packed</a>"
				}
				Body += "<tr><td><input type='checkbox' name='id' value='"+data.data[i].id+"'>\
						<td>" + data.data[i].name + "</td>\
						<td class='visible-lg visible-md visible-sm'>" + data.data[i].name + "</td>\
						<td class='relative'><span class='password' data-pw='"+data.data[i].password+"'>**********</span><span class='glyphicon glyphicon-eye-open cursor pw-ico' style='margin-left:10px'></span><span class='ico-copy cursor btcopy' style='margin-left:10px' title='Copy password' data-pw='"+data.data[i].password+"'></span></td>\
						<td class='visible-lg visible-md visible-sm'>"+isback+" | <a class='link' href=\"javascript:InputDatabase('"+data.data[i].name+"');\" title='Import database'>Import</a></td>\
						<td class='visible-lg visible-md visible-sm'><a class='linkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
						<td style='text-align:right;'>\
						<a href='javascript:;' class='link' onclick=\"AdminDatabase('"+data.data[i].name+"','"+data.data[i].name+"','"+data.data[i].password+"')\" title='Management database'>Manage</a> | \
						<a href='javascript:;' class='link' onclick=\"SetDatabaseAccess('"+data.data[i].name+"')\" title='Set access rights'>Permission</a> | \
						<a href='javascript:;' class='link' onclick=\"DataRespwd(0,'"+data.data[i].id+"','"+data.data[i].name+"')\" title='Modify the database password'>Change</a> | \
						<a href='javascript:;' class='link' onclick=\"DataDelete("+data.data[i].id+",'"+data.data[i].name+"')\" title='Delete database'>Delete</a>\
						</td></tr>"
			}
		}
		$("#DataBody").html(Body);
		$("#DataPage").html(data.page);
		$(".linkbed").click(function(){
			var dataid = $(this).attr("data-id");
			var databak = $(this).text();
			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' name='bak' value='" + databak + "' placeholder='Description' onblur='GetBakPost(\"databases\")' />");
			$(".baktext").focus();
		});
		btcopy();
		showHidePwd();
	});
}

function DataAdd(sign){
	if(sign==0){
		var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '480px',
		title: 'Add database',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<form class='zun-form-new' id='DataAdd'>\
						<div class='line'>\
							<label><span>Database Name</span></label><div class='info-r'><input  type='text' name='name' placeholder='New database name' style='width:70%' />\
							<select name='codeing' style='width:22%'>\
								<option value='utf8'>utf-8</option>\
								<option value='utf8mb4'>utf8mb4</option>\
								<option value='gbk'>gbk</option>\
								<option value='big5'>big5</option>\
							</select>\
							</div>\
						</div>\
						<div class='line'>\
						<label><span>Password</span></label><div class='info-r'><input  type='text' name='password' id='MyPassword' style='width:340px' placeholder='Database password' value='"+(RandomStrPwd(10))+"' /><span title='Random code' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(10)'></span></div>\
						</div>\
                        <div class='line'>\
						<label><span>Permission</span></label>\
						<div class='info-r'>\
						<select id='dataAccess' style='width:100px;'>\
							<option value='127.0.0.1'>Local server</option>\
							<option value='%'>Everyone</option>\
							<option value='ip'>Specify IP</option>\
						</select>\
						<input type='text' name='address' placeholder='Please enter the IP address allowed to access' style='width:230px;display:none;' />\
						</div>\
						</div>\
						<div class='line' style='display:none'>\
						<label><span>Description</span></label><div class='info-r'><input type='text' name='ps' placeholder='Database note' /></div>\
						</div>\
                        <div class='submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>Cancel</button>\
					        <button type='button' class='btn btn-info btn-sm btn-title' onclick=\"DataAdd(1)\" >Submit</button>\
				        </div>\
				      </form>"
		});

		$("#dataAccess").change(function(){
			var access = $(this).val();
			if(access == 'ip'){
				$("input[name=address]").show().val('');
			}else{
				$("input[name=address]").hide();
			}
		});
	}else{
		var loadT=layer.load({shade:true,shadeClose:false});
		var access = $("#dataAccess").val();
		if(access != 'ip') $("input[name=address]").val(access);
		var data = $("#DataAdd").serialize();
		$.post('/database?action=AddDatabase',data,function(rdata){
			if(rdata.status){
				getData(1);
				layer.closeAll();
				layer.msg(rdata.msg,{icon:1});
			}else{
				layer.closeAll();
				layer.msg(rdata.msg,{icon:2});
			}
		});
	}
}

function DataSetuppwd(sign, passwd) {
		if (sign == 0) {
			$.post('/data?action=getKey','table=config&key=mysql_root&id=1',function(rdata){
				var mypasswd=rdata;
				var index = layer.open({
				type: 1,
				skin: 'demo-class',
				area: '500px',
				title: 'Set the database password',
				closeBtn: 2,
				shift: 5,
				shadeClose: false,
				content: "<div class='zun-form-new'' id='DataSetuppwd'>\
						<div class='line'>\
						<label style='width:14%'><span>Root password:</span></label><div class='info-r'><input id='MyPassword' type='text' name='password' value='"+mypasswd+"' style='width:350px' /><span title='Random code' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span>\
						</div></div>\
				        <div class='submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>Cancel</button>\
					        <button type='button' id='PostPwBtn' class='btn btn-info btn-sm btn-title' onclick='DataSetuppwd(1)' >Submit</button>\
				        </div>\
				      </div>"
			});
			RandomStrPwd(16);
			$("#MyPassword").focus().keyup(function(e){
				if(e.keyCode == 13) $("#PostPwBtn").click();
			});
		});
		} else {
			var loadT=layer.msg('Processing, please wait...',{icon:16,time:0});
			var newPassword = $("#MyPassword").val();
			var data = 'password='+newPassword;
			$.post('/database?action=SetupPassword',data,function(rdata){
				if(rdata.status){
					getData(1);
					layer.closeAll();
					layer.msg(rdata.msg,{icon:1});
					setTimeout(function(){window.location.reload();},3000);
				}else{
					layer.close(loadT);
					layer.msg(rdata.msg,{icon:2});
				}
			});
		}
}

function DataRespwd(sign,id,username){
	if(sign==0){
		layer.open({
			type:1,
			skin:'demo-class',
			area:'500px',
			title:'Modify the database password',
			closeBtn:2,
			shift:5,
			shadeClose:false,
			content:"<form class='zun-form-new' id='DataRespwd'>\
						<div class='line'>\
						<input type='text' name='id' value='"+id+"' hidden />\
						<label><span>Username:</span></label><div class='info-r'><input type='text' name='username' value='"+username+"' readonly='readonly'/>\
						</div></div>\
						<div class='line'>\
						<label><span>New password:</span></label><div class='info-r'><input type='text' name='password' placeholder='New database password' />\
						</div></div>\
				        <div class='submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>Cancel</button>\
					        <button type='button' class='btn btn-info btn-sm btn-title' onclick='DataRespwd(1)' >Submit</button>\
				        </div>\
				      </form>"
		});
		return;
	}
	layer.confirm("Are you sure you want to change the password for the database??",{title:'Database management',closeBtn:2},function(index){
			if(index>0){
				var loadT=layer.load({shade:true,shadeClose:false});
				var data = $("#DataRespwd").serialize();
				$.post('/database?action=ResDatabasePassword',data,function(rdata){
					getData(1);
					layer.closeAll();
					layer.msg(rdata.msg,{icon:rdata.status?1:2});
				});
			}
		});

}

function DataDetails(id,dataname,page){
	if(page == undefined){
		page = '1';
	}
	var loadT = layer.msg('Getting...',{icon:16,time:0});
	$.post('/data?action=getFind','table=databases&id='+id,function(rdata){
		$.post('/data?action=getData','table=backup&search='+id+'&limit=5&p=1&type=1&tojs=DataDetails&p='+page,function(frdata){
			layer.close(loadT);
			var ftpdown = '';
			var body='';
			var port;

			frdata.page = frdata.page.replace(/'/g,'"').replace(/DataDetails\(/g,"DataDetails(" + id + ",0,");
			for(var i=0;i<frdata.data.length;i++){
				if(frdata.data[i].type == '0') continue;
				if(frdata.data[i].filename.length < 12){
					var ftpdown = "<a class='link' href='/cloud?filename="+frdata.data[i].filename+"&name="+ frdata.data[i].name+"' target='_blank'>Download</a>";
				}else{
					var ftpdown = "<a class='link' herf='javascrpit:;' onclick=\"RecoveryData('"+frdata.data[i].filename+"','"+dataname+"')\">Restore</a> | <a class='link' href='/download?filename="+frdata.data[i].filename+"&name="+ frdata.data[i].name+"' target='_blank'>Download</a>";
				}

				 body += "<tr><td><span class='glyphicon glyphicon-file'></span>"+frdata.data[i].name+"</td>\
								<td>"+(ToSize(frdata.data[i].size))+"</td>\
								<td>"+frdata.data[i].addtime+"</td>\
								<td style='color:#bbb;text-align:right'>\
								"+ftpdown+" | <a class='link' herf='javascrpit:;' onclick=\"DataBackupDelete('"+id+"','"+frdata.data[i].id+"')\">Delete</a>\
								</td>\
							</tr>"
			}


			if(dataname == 0){
				var sBody = "<table width='100%' id='DataBackupList' class='table table-hover'>\
							<thead><tr><th>File name</th><th>File size</th><th>Packing time</th><th width='140px' class='text-right'>Action</th></tr></thead>\
							<tbody id='DataBackupBody' class='list-list'>"+body+"</tbody>\
							</table>"
				$("#DataBackupList").html(sBody);
				$(".page").html(frdata.page);
				return;
			}
			layer.closeAll();
			layer.open({
					type: 1,
					skin: 'demo-class',
					area: '700px',
					title: 'Database backup details',
					closeBtn: 2,
					shift: 5,
					shadeClose: false,
					content:"<form class='zun-form' id='DataBackup' style='max-width:98%'>\
							<button class='btn btn-info btn-sm' style='margin-right:10px' type='button' onclick=\"DataBackup(" + rdata.id + ",'" + dataname + "')\">Unpack</button>\
							</form>\
							<div class='divtable' style='margin:10px 17px 17px'><table width='100%' id='DataBackupList' class='table table-hover' style='margin-bottom:0'>\
							<thead><tr><th>Backup name</th><th>File size</th><th>Backup time</th><th class='text-right'>Action</th></tr></thead>\
							<tbody id='DataBackupBody' class='list-list'>"+body+"</tbody>\
							</table><div class='page'>"+frdata.page+"</div></div>"
			});
		});
	});
}

function RecoveryData(fileName,dataName){
	layer.confirm("The database will be overwritten, continue??",{title:'Import Data',closeBtn:2},function(index){
		var loadT =layer.msg('Importing, please wait...', {icon:16,time:0,shade: [0.3, '#000']});
		$.post('/database?action=InputSql','file='+fileName+'&name='+dataName,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}

function DataBackup(id,dataname){
	var loadT =layer.msg('Backing up, please wait...', {icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=ToBackup', "id="+id, function(rdata) {
		if (rdata.status == true) {
			layer.closeAll();
			DataDetails(id,dataname);
			layer.msg('Successful operation', {
				icon: 1
			});
		} else {
			layer.closeAll();
			DataDetails(id,dataname);
			layer.msg('Operation failed', {
				icon:2
			});
		}
	});
}

function DataBackupDelete(typeid,id,dataname){
	layer.confirm("Really want to delete the backup file??",{title:'Delete backup',closeBtn:2},function(index){
		var loadT=layer.load({shade:true,shadeClose:false});
		$.post('/database?action=DelBackup','id='+id,function(frdata){
			layer.closeAll();
			layer.msg(frdata.msg,{icon:frdata.status?1:2});
			DataDetails(typeid,dataname);
		});
	});
}

function DataDelete(id,name){
	layer.open({
		type: 1,
	    title: "Delete database ["+name+"]",
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='zun-form-new webDelete'>\
	    	<p>Once deleted, it will not be recovered! Are you sure you want to delete this database?</p>\
			<div class='vcode'>Calculation results: <span class='text'></span>=<input type='text' id='vcodeResult' value=''></div>\
	    	<div class='submit-btn' style='margin-top:15px'>\
				<button type='button' id='web_end_time' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>Cancel</button>\
		        <button type='button' id='web_del_send' class='btn btn-info btn-sm btn-title'  onclick=\"ftpall('"+id+"','"+name+"')\">Submit</button>\
	        </div>\
	    </div>"
	})
	randomSum();
}

function randomSum(){
	var a = Math.round(Math.random()*9+1);
	var b = Math.round(Math.random()*9+1);
	var sum = '';
	sum = a + b;
	$(".vcode .text").text(a+' + '+b);
	setCookie("vcodesum",sum);
	$("#vcodeResult").focus().keyup(function(e){
		if(e.keyCode == 13) $("#web_del_send").click();
	});
}

function ftpall(id,name){
	var sum = $("#vcodeResult").val();
	if(sum == undefined || sum ==''){
		layer.msg("Enter the calculation result, otherwise it cannot be deleted");
		return;
	}
	else{
		if(sum == getCookie("vcodesum")){
			var loadT = layer.load();
			//'/database?action=DelLiteTable','table=databases'
			$.post('/database?action=DeleteDatabase','id='+id+'&name='+name,function(frdata){
				getData(1);
				layer.closeAll();
				layer.msg(frdata.msg,{icon:frdata.status?1:2});
			});
		}
		else{
			layer.msg("Calculation error, please recalculate");
			return;
		}
	}
}

function goSet(num){
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data='';
	var a = '';
	var count = 0;
	for(var i=0;i<len;i++){
		if(el[i].checked == true && el[i].value != 'on'){
			data += a+count+'='+el[i].value;
			a = '&';
			count++;
		}
	}
	if(num==1){
		reAdd(data);
	}
	else if(num==2){
		shift(data);
	}
}
