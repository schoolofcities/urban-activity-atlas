<script>
    import "../assets/global-styles.css"; 
    import { onMount } from 'svelte';
    import { replaceState } from '$app/navigation';
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
    let mapDimensionView = "2D" // "2D" or "3D"
    let timePeriod = '2024-2025';
    let changePeriodFrom = '';
    let changePeriodTo = '';

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

    function isOregonMetro(locationName) {
        const stateSegment = locationName.split(', ')[1];
        if (!stateSegment) {
            return false;
        }

        return stateSegment.split('-').includes('OR');
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
        replaceState(url, {});
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
        //console.log(mapDimensionView);
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




<svelte:head>

	<title>Urban Activity Atlas | School of Cities</title>

	<meta name="description" content="Explore maps of human activity levels in the 300 largest metropolitan regions in the US and Canada">
	<meta name="author" content="Julia Greenberg, Aniket Kali, Jeff Allen, Karen Chapple">

	<meta property="og:title" content="Urban Activity Atlas | School of Cities" />
	<meta property="og:description" content="Explore maps of human activity levels in the 300 largest metropolitan regions in the US and Canada" />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://schoolofcities.github.io/urban-activity-atlas" />
	<meta property="og:image" content="https://schoolofcities.github.io/urban-activity-atlas/web-card.png" />
	<meta property="og:locale" content="en_CA">

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://schoolofcities.github.io/urban-activity-atlas" />
	<meta name="twitter:creator" content="@UofTCities" />
	<meta name="twitter:title" content="Urban Activity Atlas | School of Cities" />
	<meta name="twitter:description" content="Explore maps of human activity levels in the 300 largest metropolitan regions in the US and Canada" />
	<meta name="twitter:image" content="https://schoolofcities.github.io/urban-activity-atlas/web-card.png" /> 

</svelte:head>





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
            bind:timePeriod={timePeriod}
            bind:changePeriodFrom={changePeriodFrom}
            bind:changePeriodTo={changePeriodTo}
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
            timePeriod={timePeriod}
            changePeriodFrom={changePeriodFrom}
            changePeriodTo={changePeriodTo}
            getZoomLevel={getZoomLevel}
        />
    </div>
</div>

<!-- {#if showOregonPrivacyPopup}
    <div class="modal-backdrop">
        <div class="modal" role="dialog" aria-modal="true" aria-labelledby="oregon-privacy-title">
            <h2 id="oregon-privacy-title">Oregon Data Notice</h2>
            <p>
                Oregon's Consumer Privacy Act enacted in 2025 prevents the collection of Cuebiq data. Only 2023-2024 data is shown as it was collected prior to the change.
            </p>
            <p>
                <a href={OREGON_PRIVACY_URL} target="_blank" rel="noopener noreferrer">View HB2008 on the Oregon Legislature site.</a>
            </p>
            <button type="button" class="close-modal" on:click={() => (showOregonPrivacyPopup = false)}>Close</button>
        </div>
    </div>
{/if} -->

<style>

    :global(html, body) {
        overflow-x: hidden; /* Prevent horizontal scrolling */
        width: 100vw;
        margin: 0;
        padding: 0;
    }

    a {
        color: var(--brandLightBlue);
        text-decoration: none;
        font-family: RobotoRegular;
    }

    a:visited {
        color: var(--brandLightBlue);
    }

    a:hover {
        color: var(--brandMedGreen);
        text-decoration: underline;
        cursor: pointer;
    }

    .container {
        display: flex;
    }

    .panel {
        width: 410px;
        min-width: 280px;
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

    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.55);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 3000;
        padding: 16px;
    }

    .modal {
        max-width: 520px;
        width: 100%;
        background: #111a1a;
        border: 1px solid var(--brandGray);
        border-radius: 8px;
        padding: 16px;
        color: var(--brandWhite);
    }

    .modal h2 {
        margin: 0 0 8px 0;
        font-family: TradeGothicBold;
        font-size: 1.2rem;
    }

    .modal p {
        margin: 0 0 10px 0;
        line-height: 1.35;
    }

    .close-modal {
        border: 1px solid var(--brandGray);
        background: var(--brandDarkBlue);
        color: var(--brandWhite);
        border-radius: 5px;
        padding: 8px 12px;
        cursor: pointer;
        font-family: RobotoBold;
    }

    .close-modal:hover {
        background: var(--brandLightBlue);
    }
</style>