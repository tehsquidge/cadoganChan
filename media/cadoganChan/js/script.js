/* Author: 

*/

function reply_to(number)
{
	$('#id_comment').append('@'+number+'\n');
}
function quote(number)
{
	var quote = $('#post_'+number + ' div.comment').text();
	quote = quote.replace(/(\r\n|\n|\r)/gm,"\n>");
	$('#id_comment').append('>'+ quote +'\n');
}

function highlight(number)
{
	$('#post_'+number).css('border','3px dotted red');
}

$('document').ready(function(){
	var i = location.hash.split("_");
	switch(i[0]){
		case "#quote":
			quote(i[1]);
			break;
		case "#reply":
			reply_to(i[1]);
			break;
		case "#post":
			highlight(i[1]);
	}
	
});



















