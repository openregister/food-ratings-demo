 var initialize = function () {
  var mapCanvas = document.getElementById('map-canvas'),
      coordinates = new google.maps.LatLng(51.50120605210315, -2.579009871335642),
      mapOptions = {
          center: coordinates,
          zoom: 15,
          mapTypeId: google.maps.MapTypeId.ROADMAP,
          zoomControl: true,
          zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL
          }
      },
      map = new google.maps.Map(mapCanvas, mapOptions),
      marker = new google.maps.Marker({
          position: coordinates,
          map: map,
          title: "Caspian Fish Bar"
      });
};

$(document).ready(function(){
  initialize();
});
