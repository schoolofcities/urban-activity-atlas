<script>
    import "../assets/global-styles.css"; 
    import metroRegionCentroids from '../data/metro_regions_centroids.geo.json';

    import MapView from '$lib/MapView.svelte';
    import SelectRegion from '$lib/SelectRegion.svelte';

    // Variables
    let map;
    let metroName = "";
	let pmtilesURL = "";
    let searchQuery = "";
    let dropdownOpen = false; // Initially set the dropdown as closed

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
        />
    </div>
</div>

<style>
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
    }

    .map-view {
        height: 100vh;
        width: calc(100vw - 350px);
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
