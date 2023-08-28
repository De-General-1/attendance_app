const searchInput = document.getElementById('searchInput');
const employees = document.querySelectorAll('[data-search]');
// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];


searchInput.addEventListener('input', () => {
  const searchTerm = searchInput.value.toLowerCase();
  
  employees.forEach((employee) => {
    const searchValue = employee.getAttribute('data-search').toLowerCase();
    const containsSearchTerm = searchValue.includes(searchTerm);
    
    employee.style.display = containsSearchTerm ? 'flex' : 'none';
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
  