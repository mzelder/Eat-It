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



// Geolocation
function getUserGeolocation(callback) {
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(function(position) {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;
      // Send this data to the Flask backend
      var data = sendDataToFlask(latitude, longitude, callback);
    });
  } else {
    console.log("Geolocation is not available");
  }
}

function sendDataToFlask(latitude, longitude, callback) {
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
    callback(data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}


let debounceTimer;

function showDropdown() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    actualShowDropdown();
  }, 300);
}

function actualShowDropdown() {
  var input = document.getElementById('autocomplete');
  var dropdown = document.getElementById('dropdown-menu');
  
  // Clear previous items
  dropdown.innerHTML = '';

  if (input.value.length > 0) {
      // Setting my localization option
      getUserGeolocation(function(data) {
        if (data && data.address) {
          var headerLocalization = document.createElement("h4");
          headerLocalization.textContent = "My localization";
          dropdown.appendChild(headerLocalization);
          
          var myLocationItem = document.createElement("a");
          myLocationItem.classList.add("dropdown-item");
          myLocationItem.href = "#";
          myLocationItem.textContent = data.address; // Use the received address
          dropdown.appendChild(myLocationItem);
        }
      });
    
      var service = new google.maps.places.AutocompleteService();
      service.getPlacePredictions({ input: input.value }, function(predictions, status) {
          if (status !== google.maps.places.PlacesServiceStatus.OK) {
              var error_item = document.createElement('p');
              dropdown.innerHTML = "Please enter your street and house number.";
          }
            // Add 'My Location' option
            
            // autocomplete options
            var header_autocomplete = document.createElement("h4");
            header_autocomplete.textContent = "Suggestions";
            dropdown.appendChild(header_autocomplete);
            predictions.forEach(function(prediction) {
              var item = document.createElement('a');
              item.classList.add('dropdown-item');
              item.href = '#';
              item.textContent = prediction.description;
              item.onclick = function() {
                  input.value = prediction.description;
                  dropdown.style.display = 'none';
              };
              dropdown.appendChild(item);
          });
        
          // Show dropdown
          dropdown.style.display = 'block';
      });
  } else {
      // Hide dropdown
      dropdown.style.display = 'none';
  }
}
