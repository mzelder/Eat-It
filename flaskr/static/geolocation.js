const successCallback = (position) => {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
  
    const geocoder = new google.maps.Geocoder();
    const latlng = { lat: latitude, lng: longitude };
  
    geocoder.geocode({ 'location': latlng }, function(results, status) {
      if (status === 'OK') {
        if (results[0]) {
          console.log("Address: " + results[0].formatted_address);
          // Now you have the address
          // You can display it to the user or use it as needed
        } else {
          console.log('No results found');
        }
      } else {
        console.log('Geocoder failed due to: ' + status);
      }
    });
  };
  
  const errorCallback = (error) => {
    console.log(error);
  };
  
  navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
  