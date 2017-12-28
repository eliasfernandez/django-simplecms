function showGenericRelatedObjectLookupPopup(triggeringLink) {
    var object_id = triggeringLink.id.replace(/^lookup_/, '');
    var name = id_to_windowname(object_id);
    var contenttype= object_id.replace(/object_id/, 'content_type');
    var select = $("#"+contenttype);
    
    var input = document.getElementById(object_id);
    if (select.val() === 0) {
        alert("Select a content type first.");
        return false;
    }
    var selectedItem = select.val();

    var action = "add";
    var params = "_continue=1&_popup=1";
    if(input.value !=""){
    	action = input.value;
    	
    }else{
    	params = "_popup=1"; 	
    }
    
    //cms_ctypes es el listado de tipos de contenido disponibles 

    var href = '/admin/'+cms_ctypes[selectedItem]+"/"+action+"/";
    
    if (href.search(/\?/) >= 0) {
        href = href + '&' + params;
    } else {
        href = href + '?' + params; 
    }
    var win = window.open(href, name, 'height=800,width=1200,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}


(function ($) {

    $( document ).on("django:lookup-related", function(e){
            showGenericRelatedObjectLookupPopup(e.target)
            //showAdminPopup(triggeringLink, /^lookup_/, true)
            e.preventDefault();
            
    });

}(django.jQuery))



function dismissAddAnotherPopup(win, newId, newRepr) {
    // newId and newRepr are expected to have previously been escaped by
    // django.utils.html.escape.
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem) {
        var elemName = elem.nodeName.toUpperCase();
        if (elemName == 'SELECT') {
            var o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
        } else if (elemName == 'INPUT') {
            if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                elem.value += ',' + newId;
            } else {
                elem.value = newId;
            }
        }
    } else {
        var toId = name + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    win.close();
    saveandstay();
    //console.debug ()
    //document.getElementById("page_form").submit();
}
function saveandstay(){
	//  document.getElementById("page_form").action = "?_continue=1";
    if (document.getElementById("page_form")) {
	   document.getElementById("page_form")["_continue"].click();
    } else if (document.getElementById("gallery_form")) {
       document.getElementById("gallery_form")["_save"].click();
    }
}
function sort(link, field){
	input = django.jQuery("#id_"+field);

	var i= 0;
	if(link.className=="sortup")
		up=true;
	else if(link.className=="sortdown")
		up=false;
	
	
	
	input.val(parseInt(input.val())+ (( up )? -1 : 1 ));
	if(input.val()<=0)
		input.val(1);
	
	
	var trs  = input.parent("td").parent("tr").siblings('tr');

	trs.each(function(tr){
		inp = django.jQuery(this).children("td.sorting").children("input");
		
		if(inp !=input  && inp.val()==input.val() )
			inp.val( parseInt(inp.val()) + (( up )? 1 : -1 ))
		
	});
	saveandstay();
	
}

function add_remove_action(){
    
    $(".contentdeletelink").click(function(e){
        e.preventDefault();
        $(this).next().find("input").attr("checked", true);
        if (confirm("¿Seguro que quiere borrar el contenido?"))
            saveandstay();

    })

}