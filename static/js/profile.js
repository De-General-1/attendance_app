const optionMenu = document.querySelector(".select-menu"),
selectBtn = optionMenu.querySelector(".select-btn"),
options = optionMenu.querySelectorAll(".option"),
hiddenInput = document.querySelector('#hiddenInput'),
sBtn_text = optionMenu.querySelector(".sBtn-text");
// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];



selectBtn.addEventListener("click", () => optionMenu.classList.toggle("active"));       

options.forEach(option =>{
   option.addEventListener("click", ()=>{
       let selectedOption = option.querySelector(".option-text").innerText;
       sBtn_text.innerText = selectedOption;
       hiddenInput.value = selectedOption;

       optionMenu.classList.remove("active");
       console.log(hiddenInput.value)
   });
});

// When the user clicks on the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
