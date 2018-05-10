formatFileSize = function (bytes) {
            if (typeof bytes !== 'number' || bytes === null) {
                return '';
            }
            if (bytes >= 1000000000) {
                return (bytes / 1000000000).toFixed(2) + ' GB';
            }
            if (bytes >= 1000000) {
                return (bytes / 1000000).toFixed(2) + ' MB';
            }
            return (bytes / 1000).toFixed(2) + ' KB';
        };

$(function() {
	$("input[name=type]").change(function () {
		if ($("#standardtext").attr('checked')) { $("input.standardtext").removeAttr("disabled");}
		else {$("input.standardtext").attr("disabled", true);}
	}).change();
});

	
$('#file_upload').fileUploadUI({
//     url: '/path/to/upload/handler.json'
	
	uploadTable: $('#files'),
	downloadTable: $('#files'),
	buildUploadRow: function (files, index, handler)
	{
		
            return $('<tr><td>' + files[index].name + '<\/td>' +
                    '<td class="file_upload_progress"><div><\/div><\/td>' +
                    '<td class="file_upload_cancel">' +
                    '<button class="ui-state-default ui-corner-all" title="Cancel">' +
                    '<span class="ui-icon ui-icon-cancel">Cancel<\/span>' +
                    '<\/button><\/td><\/tr>');
        },
	buildDownloadRow: function (file, handler)
	{

//             alert(file+"uuu"+downloadRow);
		var downloadRow = handler.downloadTable.find('.file_download_template:last')
			.clone().removeAttr('id').removeClass("file_download_template");
		    
		downloadRow.attr('data-id', file.id || file.name);
		downloadRow.attr('data-type', file.filetype);
		downloadRow.find('.file_name a:last')
			.text(file.name);
		downloadRow.find('.file_size:last')
			.text(formatFileSize(file.size));
		downloadRow.find('.file_sentencenumber:last')
			.text(file.sentences+" sentences.");
		if (file.thumbnail) {
			downloadRow.find('.file_download_preview:last').append(
				$('<a/>').append($('<img/>').attr('src', file.thumbnail || null))
				);
			downloadRow.find('a:last').attr('target', '_blank');
			}
		downloadRow.find('a:last')
			.attr('href', file.url || null);
		downloadRow.find('.file_view button:last')
			.button({icons: {primary: 'ui-icon-upload'}, text: false}).click(function() {
				var clicked = $(this).parent().parent().attr("data-id");
// 				alert('click'+clicked);
				enterDB(this);
			});
		return downloadRow;
		 
// 		$('.file_view')
		
        }		       
});



viewer = function(that) {
	var row = $(that).parent().parent();
	var filename = row.attr("data-id");
	var filetype = row.attr("data-type");
	$("#filename").attr("value", filename );
	$("#filetype").attr("value", filetype );
// 	$("#username").attr("value", unam );
	$("#fileform").attr("action", "viewer.cgi" );
	$("#fileform").submit();
}

enterDB = function(that) {
	var row = $(that).parent().parent();
	var filename = row.attr("data-id");
	var filetype = row.attr("data-type");
	$("#filename").attr("value", filename );
	$("#filetype").attr("value", filetype );
// 	$("#username").attr("value", unam );
	$("#fileform").attr("action", "project.cgi" );
	$("#fileform").submit();
	console.log($("#fileform"))
}

tempStorageConll = function() {
	
	
}

/*
 
var fileName = handler.formatFileName(file.name),
                fileUrl = handler.getFileUrl(file, handler),
                thumbnailUrl = handler.getThumbnailUrl(file, handler),
                downloadRow = handler.downloadTemplate
                    .clone().removeAttr('id');*/

//             return $('<tr><td>' + file.name + 'mmm<\/td><\/tr>');

/*
$(function () {
    $('#file_upload').fileUploadUI({
        uploadTable: $('#files'),
        buildUploadRow: function (files, index, handler) {
            return $('<tr><td>' + files[index].name + '<\/td>' +
                    '<td class="file_upload_progress"><div><\/div><\/td>' +
                    '<td class="file_upload_cancel">' +
                    '<button class="ui-state-default ui-corner-all" title="Cancel">' +
                    '<span class="ui-icon ui-icon-cancel">Cancel<\/span>' +
                    '<\/button><\/td><\/tr>');
        },
        buildDownloadRow: function (file, handler) {
		
            return $('<tr><td>' + file.name + 'mmm<\/td><\/tr>');
        }
    });
});*/

// $(function () {
//     // Initialize jQuery File Upload (Extended User Interface Version):
//     $('#file_upload').fileUploadUIX();
//     
//     // Load existing files:
//     $.getJSON($('#file_upload').fileUploadUIX('option', 'url'), function (files) {
//         var fileUploadOptions = $('#file_upload').fileUploadUIX('option');
//         $.each(files, function (index, file) {
//             fileUploadOptions.buildDownloadRow(file, fileUploadOptions)
//                 .appendTo(fileUploadOptions.downloadTable).fadeIn();
//         });
//     });
// });
