var docBack = document.getElementById("background");

var switchImg = window.setInterval(changeBack,1000);
var counter = 0;

function changeBack() {
 if (counter == 1) {
	counter -= 1;
	docBack.src = "images/2.gif";
 }
 else {
	counter += 1;
	docBack.src = "images/1.gif";
}
}


