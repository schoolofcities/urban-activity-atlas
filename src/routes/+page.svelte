<script>
    import "../assets/global-styles.css"; 
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    
    import MapView from '$lib/MapView.svelte';
    import SidePanel from '$lib/SidePanel.svelte';
    
    import metroRegionCentroids from '../data/metro_regions_centroids.geo.json';
    
    
    // Variables
    let map;
    let metroName = "";
	let pmtilesURL = "";
    let searchQuery = "";
    let dropdownOpen = false; // Initially set the dropdown as closed
    let mapInitialized = false;
    let mapDimensionView = "3D" // "2D" or "3D"

    // Load min/max data from the JSON file
    import minmax from '../data/min_max.json';

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

    // Convert a Metro region name to a URL friendly format, eg. "New York-Newark-Jersey City, NY-NJ-PA" --> "new-york--newark--jersey-city_ny--nj--pa"
    function getURLFormat(s) {
        return s.toLowerCase().replaceAll(", ", "_").replaceAll("-", "--").replaceAll(" -- ", "---").replaceAll(" ", "-")
    } 

    // Convert a URL friendly format back to Metro region name
    function getMetroFormat(s) {
        // Split cities and states, handle each part independently
        let [citiesPart, statesPart] = s.split('_');
        
        // Format cities: split by dash, capitalize, join, then handle special cases
        citiesPart = citiesPart.split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ')
            .replaceAll('   ', ' - ')
            .replaceAll('  ', '-');
        
        // Format states: just handle dashes and uppercase if exists
        return statesPart ? 
            `${citiesPart}, ${statesPart.replaceAll('--', '-').toUpperCase()}` : 
            citiesPart;
    }

    function getZoomLevel() {
        let curScreenSize = window.innerWidth;
        
        if (curScreenSize < 500) {  // Very zoomed out for small screens
            return {initZoom: 2.3, minZoom: 2, regionZoom: 8.5};
        } else if (curScreenSize < 800) {  // Moderately zoomed out for tablets
            return {initZoom: 3, minZoom: 2.5, regionZoom: 9};
        } else {  // Default zoom for larger screens
            return {initZoom: 3.5, minZoom: 3, regionZoom: 9.5};
        }     
    }

    // Function to handle location selection
    const selectLocation = (location) => {
        if (!mapInitialized) return; // Don't proceed if map isn't ready
        metroName = location;
        searchQuery = location; // Update the search bar with the selected location
        zoomToLocation(metroName);
        dropdownOpen = false; // Close the dropdown after selection, as applicable
        
        // Update URL without triggering a page reload
        const url = new URL(window.location);
        if (location === '') {
            url.searchParams.delete('metro'); 
        } else {
            url.searchParams.set('metro', getURLFormat(location));
        }
        history.replaceState({}, '', url); // Ignore the suggestion to use the SvelteKit imported version of replaceState - it leads to a complicated situation of trying to update the URL that doesn't seem to work
    };

    // Function to zoom to the selected location
    const zoomToLocation = (locationName) => {
        if (locationName === '') {
            map.flyTo({
                center: [-98, 45],
                zoom: getZoomLevel().initZoom,
                bearing: 0,
                pitch: 0,
                essential: true, // Smooth transition
                duration: 1000, // Transition duration in milliseconds
            });
        }

        // Find the feature by name
        const feature = metroRegionCentroids.features.find(
            (feature) => feature.properties.name === locationName
        );

        if (feature) {
            const [lon, lat] = feature.geometry.coordinates;
            if (mapDimensionView === "3D") {
                map.flyTo({
                    bearing: 40,
                    pitch: 50,
                    center: [lon - .1, lat], // Small adjustment since map is behind panel
                    zoom: getZoomLevel().regionZoom,
                    essential: true, // Smooth transition
                    duration: 1000, // Transition duration in milliseconds
                });
            } else {
                map.flyTo({
                    bearing: 0,
                    pitch: 0,
                    center: [lon - .1, lat], // Small adjustment since map is behind panel
                    zoom: getZoomLevel().regionZoom,
                    essential: true, // Smooth transition
                    duration: 1000, // Transition duration in milliseconds
                });
            }
        }
    };

    $: {
        console.log(mapDimensionView);
        if (metroName !== "") {
            zoomToLocation(metroName);
        }
    };

    // Handle map initialization
    const handleMapInit = () => {
        mapInitialized = true;
        const urlMetro = $page.url.searchParams.get('metro');
        if (!urlMetro) return;

        const fullMetro = getMetroFormat(decodeURIComponent(urlMetro));
        const exists = metroRegionCentroids.features.some(
            feature => feature.properties.name === fullMetro
        );
        
        if (exists) {
            selectLocation(fullMetro);
        }
    };
</script>




<div class="container">
    <div class="panel">
        <SidePanel 
            metroRegionCentroids={metroRegionCentroids}
            bind:searchQuery={searchQuery} 
            bind:dropdownOpen={dropdownOpen} 
            handleInputChange={handleInputChange} 
            handleSearchInputClick={handleSearchInputClick} 
            selectLocation={selectLocation}
            bind:mapDimensionView={mapDimensionView}
        />
    </div>

    <div class="map-view">
        <MapView 
            bind:map={map} 
            handleClickOutside={handleClickOutside} 
            metroName={metroName} 
            minmax={minmax}
            selectLocation={selectLocation}
            on:mapInit={handleMapInit}
            mapDimensionView={mapDimensionView}
            getZoomLevel={getZoomLevel}
        />
    </div>
</div>

<style>

    :global(html, body) {
        overflow-x: hidden; /* Prevent horizontal scrolling */
        width: 100vw;
        margin: 0;
        padding: 0;
    }

    .container {
        display: flex;
    }

    .panel {
        width: 410px;
        min-width: 280px;
        max-width: 399px;
        border-right: solid 1px var(--brandGray);
        height: 100vh;
        overflow: auto;
        overflow-x: hidden;
        background-color: #111a1a;
    }

    .map-view {
        height: 100vh;
        width: calc(100vw - 399px);
        min-width: 280px;
        background-color: var(--brandLightBlue); 
    }

    @media screen and (max-width: 820px) {
        .container {
            flex-direction: column-reverse;
        }

        .panel {
            height: calc(50vh - 1px);
            min-width: auto;
            width: 100vw;
            min-width: 299px;
            border-top: solid 1px var(--brandGray);
            border-right: none;
        }
        
        .map-view {
            height: 50vh;
            width: 100vw;
            min-width: 300px;
        }

    }

    /* Additional fixes for very small screens */
    @media screen and (max-width: 500px) {
        .panel {
            font-size: 0.9rem;
        }
    }
</style>