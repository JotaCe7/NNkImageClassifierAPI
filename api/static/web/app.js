// alert("Hello world!")
// var greeting = "Hello comander";
// // document.getElementById("title").innerHTML = greeting;
// document.getElementById("mybtn").onclick = function() {myFunction()};
// function myFunction() {
//   document.getElementById("paragraph").innerHTML = greeting;
// }



const image_input = document.querySelector("#image_input2");
var uploaded_image = ""

image_input.addEventListener("change", function() {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    uploaded_image = reader.result;
    document.querySelector("#display_image2").style.backgroundImage = `url(${uploaded_image})`;
  })
  reader.readAsDataURL(this.files[0]);
  // TODO: delete console.log
  console.log(this.files[0].name) 
})

window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;//compatibility for Firefox and chrome
var pc = new RTCPeerConnection({iceServers:[]}), noop = function(){};      
pc.createDataChannel('');//create a bogus data channel
pc.createOffer(pc.setLocalDescription.bind(pc), noop);// create offer and set local description
pc.onicecandidate = function(ice)
{
 if (ice && ice.candidate && ice.candidate.candidate)
 {
  var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];
  console.log('my IP: ', myIP);   
  pc.onicecandidate = noop;
 }
};

// const element = document.getElementById("result")
// element.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});

