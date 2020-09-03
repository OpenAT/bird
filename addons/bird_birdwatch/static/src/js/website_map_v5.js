/*
VERSION HISTORY:

website_map_v5.js
-----------------
- use a smaller map bundeslaender_und_gemeinden_min_4p.js where we made sure that no areas where removed when
  simplifying the map so no communities are left with missing areas
  https://mapshaper.org/
- Updated leaflet library to 1.6
*/

// TODO: Load Markers and geojson with leaflet plugin to speed up data set
// https://github.com/SINTEF-9012/PruneCluster
// https://github.com/Leaflet/Leaflet.markercluster


// Global Variables to hold the gardenMap and related data
var gardenMap = null;
var pruneCluster = null;

var bird_sights = [];
var bird_sights_by_species = [];
var new_marker = null;
var markerClusterGroup = null;
var mapControl = null;
var zoomControl = null;

var greenIcon = new L.Icon({
    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

$(document).ready(function () {
    'use strict';

    //----------------------------
    // GET DATA AND START INIT MAP
    //----------------------------

    // Get all data from the /gl2k/garden/data json-controller and initialize the map
    try {
        var url = "/bird/sighting/data";
        if ( $( "#bird_birdwatch_map" ).length ) {
            $.ajax({
                url: url,
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                data: JSON.stringify({"params": {}}),

                // request error
                error: function (data) {
                    console.log('Error on getting data from '+url+' !');
                },

                // request success
                success: function (data) {

                    bird_sights = data.result.bird_sightings[0];
                    bird_sights_by_species = groupCategory(bird_sights, 'bird_species_name');

                    // INITIALIZE THE MAP AFTER WE RECEIVED AND PREPARED THE DATA
                    initMap();
                }
            });
        }

    // request exception
    } catch (error) {
        console.log('Exception on getting data from '+url+' ! ', error);
    }


    //-----------------------
    // Initialize Leaflet Map
    //-----------------------

    function initMap() {
        markerClusterGroup = L.markerClusterGroup();
        mapControl = L.control.layers(null, null, {
            collapsed: false,
            position:'topright'
        });
        zoomControl = L.control.zoom({
             position:'topleft'
        });

        var cornerTop = L.latLng(49.029, 9.225),
            cornerBottom = L.latLng(46.284, 17.185),
            boundary = L.latLngBounds(cornerTop, cornerBottom);

        gardenMap = L.map('bird_birdwatch_map', {
            center: [47.564, 13.364],
            zoom: 7,
            zoomControl: false,
            maxBounds: boundary,
        });
        zoomControl.addTo(gardenMap);
        mapControl.addTo(gardenMap);

        gardenMap.addControl(new GeoSearch.GeoSearchControl({
            provider: new GeoSearch.OpenStreetMapProvider(),
            style: 'bar',
            showMarker: false,
            autoClose: true,
            searchLabel: 'Adresse eingeben',
            keepResult: true,
        }));

        var austria_bounds = [[46.35877, 8.782379], [49.037872, 17.189532]];

        var BasemapAT_highdpi = L.tileLayer('https://maps{s}.wien.gv.at/basemap/bmaphidpi/normal/google3857/{z}/{y}/{x}.{format}', {
            maxZoom: 14,
            minZoom: 7,
            attribution: 'Datenquelle: <a href="https://www.basemap.at">basemap.at</a>',
            subdomains: ["", "1", "2", "3", "4"],
            format: 'jpeg',
            bounds: austria_bounds
        });
        gardenMap.addLayer(BasemapAT_highdpi);

        gardenMap.on('click', onMapClick);
        createMarker();
    }

    function onMapClick(e) {
        // Remove existing clicked_marker first
        if (new_marker) {
            new_marker.remove();
            new_marker = null;
        }
        // Add new clicked_marker
        new_marker = L.marker(e.latlng, {icon: greenIcon}).addTo(gardenMap);
        // Fill the form fields with lng and lat values
        $('#longitude').val(e.latlng.lng);
        $('#latitude').val(e.latlng.lat);
    }

    function onMarkerClick(e){
        var el = $(e.srcElement || e.target),
        id = el.attr('id');
        var popup = e.target.getPopup();
        var url = "/bird/sighting/image";
        $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            data: JSON.stringify({"params": {"bird_sighting_record_ids": [id]}}),
            // request error
            error: function (data) {
                console.log('Error on getting data from '+url+' !');
            },
            // request success
            success: function (data) {
                var text = popup.getContent();
                var img_src = data.result.thumbnail_urls[id];
                text = text.replace('Lade Bild...', '<img src="'+img_src+'"/>');
                popup.setContent(text);
                popup.update();
            }
        });

    }

    function createMarker() {
        markerClusterGroup.addTo(gardenMap);
        for (var specie in bird_sights_by_species) {
            var group = L.featureGroup.subGroup(markerClusterGroup);
            bird_sights_by_species[specie].forEach(function(bird_sight){
                var longitude = bird_sight.longitude;
                var latitude = bird_sight.latitude;
                var marker = L.marker([latitude, longitude]);
                marker.id = bird_sight.id;
                marker.bindPopup("<div>Sichtungen: "+bird_sight.bird_count+"</div><div>Lade Bild...</div>");
                marker.on('click', onMarkerClick);
                marker.addTo(group);
            });
            mapControl.addOverlay(group, specie);
            group.addTo(gardenMap);
        }
    }

    function groupCategory(data, category){
        var categories = {}
        for(var record in data) {
            if (data[record][category] in categories){
                categories[data[record][category]].push(data[record]);
            } else {
                categories[data[record][category]] = [data[record]];
            }
        }
        return categories;
    }

});
