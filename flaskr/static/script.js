// Registration Validation
(() => {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')
  const password = document.getElementById("password")
  const confirm_password = document.getElementById("confirm_password")


  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
})()

// Alert after registration 
document.addEventListener('DOMContentLoaded', (event) => {
setTimeout(() => {
      var alerts = document.querySelectorAll('.alert');
      alerts.forEach(function(alert) {
          var bsAlert = new bootstrap.Alert(alert);
          bsAlert.close();
      });
  }, 3000);
});


// Address finder
let autocomplete;
function initMap() {
    autocomplete = new google.maps.places.Autocomplete(document.getElementById("autocomplete"));
}


function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

// prevent form submission if image dimensions are not okay
document.getElementById('imageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                const width = img.naturalWidth;
                const height = img.naturalHeight;
                const feedbackElement = document.getElementById('dimensionFeedback');
                if (height >= 200 && width >= 100) {
                    feedbackElement.textContent = ''; // Clear feedback if dimensions are okay
                } else {
                    feedbackElement.textContent = 'Image height must be equal or bigger than 200px and width equal or bigger than 100px.';
                    event.target.value = ''; // Reset file input
                }
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// prevent form submission if image is not selected
document.getElementById('updateButton').addEventListener('click', function(event) {
    var imageInput = document.getElementById('imageInput');
    var feedbackDiv = document.getElementById('dimensionFeedback');

    if (imageInput.files.length === 0) {
        event.preventDefault(); // Stop the form from submitting
        feedbackDiv.textContent = 'Please choose an image before updating.'; // Display error message
    } else {
        feedbackDiv.textContent = ''; // Clear any previous error message
    }
});