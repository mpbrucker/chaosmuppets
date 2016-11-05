var docBack = document.querySelector("body");

var switchImg = window.setInterval(changeBack,1000);
var counter = 0;
var bg = new SuperGif


function changeBack() {
 if (counter == 1) {
	counter -= 1;
	docBack.style.background = 'url(http://68.media.tumblr.com/009ae11093077f4236756e33092bdea3/tumblr_og14efF4Bo1qie9jco1_500.gif) no-repeat center center fixed';
 	docBack.style.backgroundSize = 'cover';
 }
 else {
	counter += 1;
	docBack.style.background = 'url(https://media.giphy.com/media/xTiTnwj1LUAw0RAfiU/giphy.gif) no-repeat center center fixed';
	docBack.style.backgroundSize = 'cover'; 
}
}

	
