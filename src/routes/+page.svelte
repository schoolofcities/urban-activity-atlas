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
    let searchQuery = "";
    let dropdownOpen = false; // Initially set the dropdown as closed

    // Load min/max data from the JSON file
    import minmax from '../data/min_max.json';

    // Sort the features alphabetically by name
    metroRegionCentroids.features.sort((a, b) =>
        a.properties.name.localeCompare(b.properties.name)
    );

    let filteredOptions = metroRegionCentroids.features;

    // Filter the options based on the search query
    $: filteredOptions = metroRegionCentroids.features.filter((feature) =>
        feature.properties.name.toLowerCase().startsWith(searchQuery.toLowerCase())
    );

    // Close the dropdown when clicking outside of it
    const handleClickOutside = (event) => {
        if (!event.target.closest('.dropdown-container')) {
            dropdownOpen = false;
        }
    };

    // Handle click inside the input field to reset the search query
    const handleSearchInputClick = () => {
        if (!searchQuery) {
            dropdownOpen = true;  // Open dropdown if nothing is typed
        } else {
            searchQuery = '';  // Clear the text if there is any
        }
    };

    // Handle input field updates (keep the dropdown open if text is typed)
    const handleInputChange = () => {
        if (searchQuery) {
            dropdownOpen = true;  // Ensure dropdown stays open when typing
        }
    };

    // Function to handle location selection
    const selectLocation = (location) => {
        metroName = location;
        searchQuery = location; // Update the search bar with the selected location
        zoomToLocation(metroName);
        dropdownOpen = false; // Close the dropdown after selection
    };

    // Function to zoom to the selected location
    const zoomToLocation = (locationName) => {
        // Find the feature by name
        const feature = metroRegionCentroids.features.find(
            (feature) => feature.properties.name === locationName
        );

        if (feature) {
            const [lon, lat] = feature.geometry.coordinates;
            map.flyTo({
                center: [lon - .1, lat], // Small adjustment since map is behind panel
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

            const minmax_metro = minmax[metroName]; // Get min & max values for region
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
                            ["cubic-bezier", 0.1, 0.01, 1.0, 1.0], // ["exponential", 2], // https://maplibre.org/maplibre-style-spec/expressions/#interpolate - NEED TO FIX THIS
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

        document.addEventListener('click', handleClickOutside);

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
            center: [-104.048, 44.511],
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
        <p id="authors">Created by Julia Greenberg, Jeff Allen, and Aniket Kali</p>
        <hr>
        <p class="description">
            Use this tool to explore activity levels in the 300 largest metropolitan regions in the US and Canada. This analysis uses cell phone data from <a href="https://spectus.ai/" target="_blank" rel="noopener noreferrer">Spectus</a> for the year-long period between April 1, 2023 and March 31, 2024.
            <br><br>
            <i>Check out our <a href="https://github.com/schoolofcities/urban-activity-atlas/blob/main/README.md" target="_blank" rel="noopener noreferrer">Github</a> for more information about our methodology.</i>
        </p> 
        <hr>
        <label for="locations" class="location-label">Choose a metropolitan region:</label>

        <div class="dropdown-container">
            <div class="dropdown-toggle" on:click={() => { if (!searchQuery) dropdownOpen = true; }}>
                <input
                    type="text"
                    class="search-input"
                    bind:value={searchQuery}
                    placeholder={searchQuery ? '' : 'Search location...'}
                    on:input={handleInputChange}
                    on:click={handleSearchInputClick}
                />
            </div>
        
            {#if dropdownOpen}
                <div class="dropdown-list">
                    {#if searchQuery === ''}
                        {#each metroRegionCentroids.features as feature}
                            <div
                                class="dropdown-item"
                                on:click={() => selectLocation(feature.properties.name)}
                            >
                                {feature.properties.name}
                            </div>
                        {/each}
                    {:else}
                        {#if filteredOptions.length > 0}
                            {#each filteredOptions as feature}
                                <div
                                    class="dropdown-item"
                                    on:click={() => selectLocation(feature.properties.name)}
                                >
                                    {feature.properties.name}
                                </div>
                            {/each}
                        {:else}
                            <div class="no-results">No results found</div>
                        {/if}
                    {/if}
                </div>
            {/if}
        </div>

        <div class="legend">
            <p class="legend-title">Activity level:</p>
            <div class="gradient-bar"></div>  
            <ul class="legend-label">
                <li class="low">Low</li>
                <li class="high">High</li>
            </ul>
        </div>       
    </div>

    <div id="map">
    </div>
</div>

<style>
    h2 {
        font-size: 2rem;
        text-align: left;
        margin: 15px 15px 15px 15px;
        font-family: RobotoRegular;
        color: white;
    }

    #authors {
        font-size: .8rem;
        line-height: 1.2;
        text-align: left;
        margin: 15px;
        font-family: RobotoRegular;
    }

    .description {
        color: white;
        margin: 15px 15px;
        line-height: 1.2;
        font-size: .8rem;
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
        font-size: .8rem;
    }

    #locations {
        display: block;
        width: calc(100% - 30px);
        margin: 8px 0 0  15px;
    }

    .legend {
        list-style: none;
        padding: 0;
        margin: 0 15px 15px 15px;
        font-family: RobotoRegular;
        font-size: .8rem;
        display: flex;
        flex-direction: column;
        align-items: left;
    }

    .legend-title {
        font-family: RobotoRegular;
        margin-bottom: 0px;
        font-size: .8rem;
    }

    .gradient-bar {
        width: 100%;
        height: 10px;
        background: linear-gradient(to right, #0b513f, #397c53, #70a863, #b2d372, #fffb85);
        margin-bottom: 5px;
    }

    .legend-label {
        display: flex; 
        justify-content: space-between;
        width: 100%;
        list-style: none;
        padding: 0;
        margin: 0;
        font-family: RobotoRegular;
        color: white;
    }

    .low {
        text-align: left;
        flex: 1;
    }

    .high {
        text-align: right;
        flex: 1;
    }

    .dropdown-container {
        position: relative;
        margin: 0 15px 0 15px;
    }

    .dropdown-toggle {
        width: 100%;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .search-input {
        width: 100%;
        margin-top: 5px;
        margin-bottom: 5px;
        font-family: RobotoRegular;
    }

    .dropdown-list {
        position: absolute;
        top: 40px;
        left: 0;
        right: 0;
        background-color: white;
        max-height: 200px;
        overflow-y: auto;
        z-index: 10;
    }

    .dropdown-item {
        padding: 3px;
        font-family: RobotoRegular;
        font-size: .8rem;
        cursor: pointer;
    }

    .dropdown-item:hover {
        background-color: #f0f0f0;
    }

    .no-results {
        padding: 8px;
        color: gray;
    }

    .container {
        display: flex;
    }

    .panel {
        width: 350px;
        position: absolute;
        background-color: #1f1f1f;
        z-index: 1;
    }

    #map {
        height: 100%;
        width: 100%;
        position: absolute;
        z-index: -99;
    }
</style>
