<script>
    import "../assets/global-styles.css"; 
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    
    import MapView from '$lib/MapView.svelte';
    import SelectRegion from '$lib/SelectRegion.svelte';
    
    import metroRegionCentroids from '../data/metro_regions_centroids.geo.json';
    
    // Variables
    let map;
    let metroName = "";
	let pmtilesURL = "";
    let searchQuery = "";
    let dropdownOpen = false; // Initially set the dropdown as closed
    let mapInitialized = false;

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

    // Function to handle location selection
    const selectLocation = (location) => {
        if (!mapInitialized) return; // Don't proceed if map isn't ready
        metroName = location;
        searchQuery = location; // Update the search bar with the selected location
        zoomToLocation(metroName);
        dropdownOpen = false; // Close the dropdown after selection, as applicable
        
        // Update URL without triggering a page reload
        const url = new URL(window.location);
        url.searchParams.set('metro', getURLFormat(location));
        history.replaceState({}, '', url);
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

    // Handle map initialization
    const handleMapInit = () => {
        mapInitialized = true;
        // Check URL params only once after map is ready
        const urlMetro = $page.url.searchParams.get('metro');
        if (urlMetro) {
            // Decode the URL parameter to get the full metro name
            const decodedMetro = decodeURIComponent(urlMetro);
            const fullMetro = getMetroFormat(decodedMetro);
            // console.log('URL Metro:', urlMetro);
            // console.log('Decoded Metro:', decodedMetro);
            // console.log('Full Metro:', fullMetro);
            const exists = metroRegionCentroids.features.some(
                feature => feature.properties.name === fullMetro
            );
            if (exists) {
                selectLocation(fullMetro);
            }
        }
    };
</script>

<div class="container">
    <div class="panel">
        <SelectRegion 
            metroRegionCentroids={metroRegionCentroids}
            bind:searchQuery={searchQuery} 
            bind:dropdownOpen={dropdownOpen} 
            handleInputChange={handleInputChange} 
            handleSearchInputClick={handleSearchInputClick} 
            selectLocation={selectLocation}
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
        />
    </div>
</div>

<style>
    .container {
        display: flex;
    }

    .panel {
        width: 399px;
        min-width: 399px;
        border-right: solid 1px var(--brandGray);
        height: 350px;
        height: 100vh;
        overflow: auto;
        overflow-x: hidden;
        background-color: #111a1a;
    }

    .map-view {
        height: 100vh;
        width: calc(100vw - 400px);
        min-width: 350px;
        background-color: var(--brandLightBlue); 
    }

    @media screen and (max-width: 820px) {
        .container {
            flex-direction: column-reverse;
        }
        
        .map-view {
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
