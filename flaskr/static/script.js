// Example starter JavaScript for disabling form submissions if there are invalid fields
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

document.addEventListener('DOMContentLoaded', (event) => {
  setTimeout(() => {
      var alerts = document.querySelectorAll('.alert');
      alerts.forEach(function(alert) {
          var bsAlert = new bootstrap.Alert(alert);
          bsAlert.close();
      });
  }, 3000);
});


// Geolocation
if ("geolocation" in navigator) {
  navigator.geolocation.getCurrentPosition(function(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    // Send this data to the Flask backend
    sendDataToFlask(latitude, longitude);
  });
} else {
  console.log("Geolocation is not available");
}

function sendDataToFlask(latitude, longitude) {
  fetch('/process_location', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ latitude: latitude, longitude: longitude }),
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

// Search bar index page
let autocomplete;
function initMap() {
  autocomplete = new google.maps.places.AutocompleteService(
    document.getElementById("autocomplete"),
    {
      types: ["establishment"],
      componentRestrictions: {"country": ["PL"]},
      fields: ["place_id", "geometry", "name"]
    });
}