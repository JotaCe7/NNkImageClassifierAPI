// alert("Hello world!")
var greeting = "Hello comander";
// document.getElementById("title").innerHTML = greeting;
document.getElementById("mybtn").onclick = function() {myFunction()};
function myFunction() {
  document.getElementById("paragraph").innerHTML = greeting;
}