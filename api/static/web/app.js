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

// const element = document.getElementById("result")
// element.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});

