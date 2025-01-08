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

    // Load quintiles data from the JSON file
    import quintiles from '../data/quintile_thresholds.json';
    // console.log(quintiles);

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
					console.log(`Removing metro layer: ${layer.id}`);
					map.removeLayer(layer.id);
				}
			});

			// Remove all metro sources
			Object.keys(map.style.sourceCaches).forEach((sourceId) => {
				if (sourceId !== 'protomaps' && map.getSource(sourceId)) {
					console.log(`Removing metro source: ${sourceId}`);
					map.removeSource(sourceId);
				}
			});

			pmtilesURL = `http://localhost:5173/metro_region_geohash_stops_pm/${metroName.replace(/ /g, '%20')}.pmtiles`;

			// console.log('pmtilesURL: ', pmtilesURL);

			// Add the PMTiles source
			map.addSource(metroName, {
                type: "vector",
                url: `pmtiles://${pmtilesURL}`,
            });

            const quintiles_metro = quintiles[metroName];
            console.log('quintiles_metro:', quintiles_metro);

            map.addLayer({
                    id: layerId,
                    type: "fill",
                    source: metroName,
                    "source-layer": metroName.replace(/[^\w]/g, ""),
                    paint: {
                        "fill-opacity": 0.65,
                        "fill-color": [
                            "step",
                            ["get", "prop_subset_stops"],
                            "#0b513f", quintiles_metro[0],
                            "#397c53", quintiles_metro[1],
                            "#70a863", quintiles_metro[2],
                            "#b2d372", quintiles_metro[3],
                            "#fffb85",
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
    </div>

    <div id="map">
    </div>
</div>

<style>
    .location-label {
        display: block;
        margin: 15px 0 0 15px;
    }

    #locations {
        width: 90%;
        margin: 8px 15px 15px 15px;
    }

    .legend {
        list-style: none;
        padding: 0;
        margin: 15px;		
    }

    .legend li {
        display: flex;
        align-items: center;
        margin: 3px;
    }
    
    .legend span {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 10px;
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
        background-color: var(--brandWhite); 
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
