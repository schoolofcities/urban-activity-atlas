<script>
    import "../assets/global-styles.css";
    import { onMount } from "svelte";
    import * as maplibregl from "maplibre-gl"; 
    import "maplibre-gl/dist/maplibre-gl.css";
    import * as pmtiles from "pmtiles";
    import layers from 'protomaps-themes-base'; 

    import metroRegionCentroids from '../assets/metro_regions_centroids.geo.json';

    let map = null;
    let metroName = "";
	let pmtilesURL = "";

    // Load min/max data from the JSON file
    import minmax from '../data/min_max.json';

    // Sort the features alphabetically by name
    metroRegionCentroids.features.sort((a, b) =>
        a.properties.name.localeCompare(b.properties.name)
    );

    // Function to zoom to the selected location
    const zoomToLocation = (locationName) => {
        // Find the feature by name
        const feature = metroRegionCentroids.features.find(
            (feature) => feature.properties.name === locationName
        );

        if (feature) {
            const [lon, lat] = feature.geometry.coordinates;
            map.flyTo({
                center: [lon, lat],
                zoom: 9,
                essential: true, // Smooth transition
                duration: 1000, // Transition duration in milliseconds
            });
        }
    };

	// Reactive to dynamically update the map when metroName changes
	$: {
        if (map && metroName) {

            // console.log('Adding source and layer for', metroName);
            const layerId = `${metroName}-layer`;

			// Remove all metro layers
			map.getStyle().layers.forEach((layer) => {
				if (layer.id.endsWith('-layer') && map.getLayer(layer.id)) {
					// console.log(`Removing metro layer: ${layer.id}`);
					map.removeLayer(layer.id);
				}
			});

			// Remove all metro sources
			Object.keys(map.style.sourceCaches).forEach((sourceId) => {
				if (sourceId !== 'protomaps' && map.getSource(sourceId)) {
					// console.log(`Removing metro source: ${sourceId}`);
					map.removeSource(sourceId);
				}
			});

            pmtilesURL = `http://localhost:5173/metro_region_geohash_stops_pm/${metroName.replace(/ /g, '%20')}.pmtiles`;

			console.log('pmtilesURL: ', pmtilesURL);

			// Add the PMTiles source
			map.addSource(metroName, {
                type: "vector",
                url: `pmtiles://${pmtilesURL}`,
            });

            // Calculate the min and max values for the selected metro region
            const metroRegion = metroRegionCentroids.features.find(feature => feature.properties.name === metroName);
            let minVal = Infinity;
            let maxVal = -Infinity;

            if (metroRegion) {
                metroRegion.geometry.coordinates.forEach(coord => {
                    const value = coord.prop_subset_stops;
                    if (value < minVal) minVal = value;
                    if (value > maxVal) maxVal = value;
                });
            }

            console.log(`Min value: ${minVal}, Max value: ${maxVal}`);

            const minmax_metro = minmax[metroName];
            console.log('minmax_metro:', minmax_metro);

            map.addLayer({
                    id: layerId,
                    type: "fill",
                    source: metroName,
                    "source-layer": metroName.replace(/[^\w]/g, ""),
                    paint: {
                        "fill-opacity": 0.65,
                        "fill-color": [
                            "interpolate", 
                            ["linear"], 
                            ["get", "prop_subset_stops"], 
                            minmax_metro[0], "#0b513f",    // Lower value - green
                            minmax_metro[1], "#fffb85"     // Higher value - yellow
                        ],
                        "fill-outline-color": "rgba(0, 0, 0, 0)",
                    },
                });
		}
    }

    onMount(() => {
        let protocol = new pmtiles.Protocol();
        maplibregl.addProtocol("pmtiles", protocol.tile);

        map = new maplibregl.Map({
            container: "map", 
            style: {
                version: 8,
                glyphs: 'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
                sprite: "https://protomaps.github.io/basemaps-assets/sprites/v4/dark",
                sources: {
                    'protomaps': {
                        type: 'vector',
                        url: 'https://api.protomaps.com/tiles/v4.json?key=f1d93c3bd5c79742',
                        attribution: '<a href="https://protomaps.com">Protomaps</a> © <a href="https://openstreetmap.org">OpenStreetMap</a>'
                    }
                },
                layers: layers("protomaps", "dark") 
            },
            center: [-96.435, 41.899],
            zoom: 3.5,
            maxZoom: 16,
            minZoom: 2,
            attributionControl: true
        });

        map.addControl(new maplibregl.NavigationControl(), "top-right");
        map.addControl(new maplibregl.ScaleControl(), "bottom-right");
    });
</script>

<div class="container">
    <div class="panel">
        <h2>Urban Activity Atlas</h2>
        <!-- <h2>Which parts of a metro region have the most activity?</h2> -->
        <p id="authors">Created by Julia Greenberg, Jeff Allen, and Aniket Kali</p>
        <hr>
        <label for="locations" class="location-label">Choose a metropolitan region:</label>
        <select id="locations" on:change="{(e) => {
            metroName = e.target.value; 
			// console.log('metroName in on:change handler: ', metroName);
            zoomToLocation(metroName); // Zoom to selected location
        }}">
            <option value="">Select a location</option>
            {#each metroRegionCentroids.features as feature}
                <option value="{feature.properties.name}">{feature.properties.name}</option>
            {/each}
        </select>

        <ul class="legend">
            <li><span style="background-color: #0b513f;"></span>Low for the region</li>
            <li><span style="background-color: #397c53;"></span></li>
            <li><span style="background-color: #70a863;"></span></li>
            <li><span style="background-color: #b2d372;"></span></li>
            <li><span style="background-color: #fffb85;"></span>High for the region</li>
        </ul>
        <hr>
        <p class="description">
            Use this tool to explore activity levels between April 1, 2023 and March 31, 2024 in the 300 largest metropolitan regions in the US and Canada. Analysis uses cell phone data from <a href="https://spectus.ai/" target="_blank" rel="noopener noreferrer">Spectus</a>.
            <br><br>
            Check out our <a href="https://github.com/schoolofcities/urban-activity-atlas/blob/main/README.md" target="_blank" rel="noopener noreferrer">Github</a> for more information about our methodology.
        </p>
    </div>

    <div id="map">
    </div>
</div>

<style>
    h2 {
        font-size: 2rem;
        text-align: left;
        margin: 30px 15px 15px 15px;
        font-family: RobotoRegular;
        color: white;
    }

    /* h2 {
        font-size: .75rem;
        text-align: left;
        margin: 15px;
        font-family: Arial, sans-serif;
        color: white;
    } */

    #authors {
        font-size: .8rem;
        line-height: 1.2;
        margin: 15px;
        font-family: RobotoRegular;
    }

    .description {
        color: white;
        margin: 15px;
        line-height: 1.2;
        font-size: 1rem;
        font-family: RobotoRegular;
    }

    /* Default state (unvisited link) */
    a {
        color: #fffb85;
        text-decoration: none;
        font-family: RobotoRegular;
    }

    /* Visited link */
    a:visited {
        color: #fffb85;
        font-family: RobotoRegular;
    }

    /* Hover state (when the link is hovered over) */
    a:hover {
        color: #70a863;
        text-decoration: underline;
        font-family: RobotoRegular;
    }

    /* Active state (when the link is clicked) */
    a:active {
        color: #70a863;
        font-family: RobotoRegular;
    }

    .location-label {
        display: block;
        margin: 15px 0 0 15px;
        color: white;
        font-family: RobotoRegular;
    }

    #locations {
        width: 90%;
        margin: 8px 15px 15px 15px;
    }

    .legend {
        list-style: none;
        padding: 0;
        margin: 15px;
        font-family: RobotoRegular;
        display: flex;
        align-items: center;
        width: 100%;
    }

    .legend li {
        flex: 1;
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-family: RobotoRegular;
        padding: 10px;
    }

    .legend::before {
        content: "";
        display: block;
        height: 10px;
        width: 100%;
        background: linear-gradient(to right, #0b513f, #397c53, #70a863, #b2d372, #fffb85);
    }

    .legend li span {
        display: none;  /* Remove the individual color boxes */
    }

    .legend li:first-child {
        padding-left: 0;
    }

    .legend li:last-child {
        padding-right: 0;
    }

    select {
        background-color: #1f1f1f;
        color: white;
        font-size: 1rem; 
        padding: 5px 5px;
        width: 200px;       
        appearance: none;   
        -webkit-appearance: none;
        -moz-appearance: none;
    }

    select option {
        background-color: #444; 
        color: white;     
        padding: 10px;          
    }

    select option:hover {
        background-color: #1f1f1f; 
    }

    select:focus {
        background-color: #1f1f1f;
        color: white;
        outline: none;       
    }

    select::-ms-expand {
        display: none;
    }

    select::-webkit-dropdown-button {
        display: none; 
    }

    .container {
        display: flex;
    }

    .panel {
        width: 350px;
        min-width: 350px;
        height: 350px;
        height: 100vh;
        overflow: auto;
        overflow-x: hidden;
        background-color: #1f1f1f;
        /*background-color: var(--brandWhite); */
    }

    #map {
        height: 100vh;
        width: calc(100vw - 350px);
        min-width: 350px;
        background-color: var(--brandLightBlue); 
    }

    @media screen and (max-width: 820px) {
        .container {
            flex-direction: column-reverse;
        }

        #map {
            height: 50vh;
            width: 100vw;
        }

        .panel {
            height: calc(50vh - 1px);
            width: 100vw;
            border-top: solid 1px var(--brandGray);
            border-right: none;
        }
    }
</style>
