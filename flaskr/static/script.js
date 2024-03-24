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



function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


if (window.location.pathname === "/admin/settings") {
    // BACKGROUND IMAGE VALIDATION 
    // prevent form submission if image dimensions are not okay
    document.getElementById('backgroundInput').addEventListener('change', function(event) {
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
                        feedbackElement.textContent = 'Image width and height must be equal or bigger than 200px';
                        event.target.value = ''; // Reset file input
                    }
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // prevent form submission if image is not selected
    document.getElementById('backgroundUpdate').addEventListener('click', function(event) {
        var imageInput = document.getElementById('backgroundInput');
        var feedbackDiv = document.getElementById('dimensionFeedback');

        if (imageInput.files.length === 0) {
            event.preventDefault(); // Stop the form from submitting
            feedbackDiv.textContent = 'Please choose an image before updating.'; // Display error message
        } else {
            feedbackDiv.textContent = ''; // Clear any previous error message
        }
    });

    // LOGO IMAGE VALIDATION 
    // prevent form submission if image dimensions are not okay
    document.getElementById('logoInput').addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const width = img.naturalWidth;
                    const height = img.naturalHeight;
                    const feedbackElement = document.getElementById('dimensionFeedback2');
                    if (height >= 80 && width >= 80) {
                        feedbackElement.textContent = ''; // Clear feedback if dimensions are okay
                        console.log('Image dimensions are okay');
                    } else {
                        feedbackElement.textContent = 'Image width and height must be equal or bigger than 80px';
                        event.target.value = ''; // Reset file input
                    }
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // prevent form submission if image is not selected
    document.getElementById('logoUpdate').addEventListener('click', function(event) {
        var imageInput = document.getElementById('logoInput');
        var feedbackDiv = document.getElementById('dimensionFeedback2');

        if (imageInput.files.length === 0) {
            event.preventDefault(); // Stop the form from submitting
            feedbackDiv.textContent = 'Please choose an image before updating.'; // Display error message
        } else {
            feedbackDiv.textContent = ''; // Clear any previous error message
        }
    });
}

/*
    CHECKOUT PAGE
*/

if (window.location.pathname === "/checkout") {
    document.addEventListener("DOMContentLoaded" , function() {
        getTimes();
    });

    function getTimes() {
        // generating time values for the select element
        var select = document.getElementById("specifyTime");
        let times = [];
        var currentTime = new Date();
        currentTime.setHours(12);
        var closingTime = 22;
        let hour = currentTime.getHours();
        let minutes = currentTime.getMinutes();


        // Checking if minutes are bigger than 30
        if (minutes >= 30) {
            hour++;
            minutes = 0;
        }
        else {
            minutes = 30;
        }

        // Creating list with all times 
        let time = (minutes == 0) ? true : false;
        for (let i = hour; i < closingTime; i++) {
            if (time) {
                times.push(`${i}:${"00"}`);
                time = false;
            }
            if (!time) {
                times.push(`${i}:${"30"}`);
                time = true;
            }
        }

        // Adding the times to the select element
        times.forEach(function(time) {
            var option = document.createElement("option");
            option.text = time;
            select.add(option);
        });
    }

    // Updating delivery time on checkout page
    document.getElementById("timeBtn").addEventListener("click", function() {
        var time = document.getElementById("specifyTime").value;
        var deliveryTime = document.getElementById("deliveryTime");
        var deliveryTimeInput = document.getElementById("deliveryTimeInput");
        
        deliveryTime.textContent = time;
        deliveryTimeInput.value = time;
    });

    document.getElementById("cash").addEventListener("click", function() {
        var cashIcon = document.getElementById("cashIcon");
        var cardIcon = document.getElementById("cardIcon");

        cashIcon.style.visibility = "visible";
        cardIcon.style.visibility = "hidden";
    });

    document.getElementById("card").addEventListener("click", function() {
        var cashIcon = document.getElementById("cashIcon");
        var cardIcon = document.getElementById("cardIcon");

        cashIcon.style.visibility = "hidden";
        cardIcon.style.visibility = "visible";
    });

    // Updating payment method on checkout page
    document.getElementById("paymentBtn").addEventListener("click", function() {
        var paymentMethodImg = document.getElementById("paymentMethodImg");
        var paymentMethodText = document.getElementById("paymentMethodText");
        var paymentMethodInput = document.getElementById("paymentMethodInput");

        var cashIcon = document.getElementById("cashIcon");
        var cardIcon = document.getElementById("cardIcon");

        if (cashIcon.style.visibility == "visible") {
            paymentMethodImg.src = "/static/images/money1.png";
            paymentMethodText.textContent = "Cash";
            paymentMethodInput.value = "Cash";
        }
        else if (cardIcon.style.visibility == "visible") {
            paymentMethodImg.src = "/static/images/card1.png";
            paymentMethodText.textContent = "Credit Card";
            paymentMethodInput.value = "Credit Card";
        }
    });
}
