<script>

    import logo from '../assets/top-logo-full.svg';

    // Props
    export let metroRegionCentroids;
    export let searchQuery;
    export let dropdownOpen;
    export let handleInputChange;
    export let handleSearchInputClick;
    export let selectLocation;
    
    // Sort the features alphabetically by name
    metroRegionCentroids.features.sort((a, b) =>
        a.properties.name.localeCompare(b.properties.name)
    );

    let filteredOptions = metroRegionCentroids.features;

    // Filter the options based on the search query
    $: filteredOptions = metroRegionCentroids.features.filter((feature) =>
        feature.properties.name.toLowerCase().startsWith(searchQuery.toLowerCase())
    );
</script>

<div>
    <h1>Urban Activity Atlas</h1>
    <p id="authors"><a>Julia Greenberg</a>, <a>Aniket Kali</a>, <a>Jeff Allen</a>, <a>Karen Chapple</a></p>
    <hr>
    <p class="description">
        Use this tool to explore human activity levels in the 300 largest metropolitan regions in the US and Canada. 
    </p> 

    <!-- <p class="location-label">Select a metropolitan region:</p> -->
    <div class="dropdown-container">
        <div class="dropdown-toggle" on:click={() => { if (!searchQuery) dropdownOpen = true; }}>
            <input
                type="text"
                class="search-input"
                bind:value={searchQuery}
                placeholder={searchQuery ? '' : 'Search metropolitan region...'}
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

    <p class="description">
        The colour of the grid pertains to how many people stopped or visited for the year-long period between April 1, 2023 and March 31, 2024. Data presented are normalized by the total activity in each metropolitan region.
        <br>
    </p> 
    

    <div class="legend">
        <p class="legend-title">Activity Level:</p>
        <div class="gradient-bar"></div>  
        <ul class="legend-label">
            <li class="low">Low</li>
            <li class="high">High</li>
        </ul>
    </div>    

    <hr>
    <p class="description">
        <i>The activity data on the map is derived from mobile phone data via <a href="https://spectus.ai/" target="_blank" rel="noopener noreferrer">Spectus</a>. Other reference data on the map are from <a href="https://www.openstreetmap.org/" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> via <a href="https://protomaps.com/" target="_blank" rel="noopener noreferrer">Protomaps</a>. Check out our <a href="https://github.com/schoolofcities/urban-activity-atlas/blob/main/README.md" target="_blank" rel="noopener noreferrer">Github</a> for more information about the data and methods.</i>
    </p>

    <div id="logo">
		<a href="https://www.schoolofcities.utoronto.ca/"><img src={logo} alt="School of Cities"></a>
	</div>
    
</div>

<style>

    #logo {
        width: 100%;
        max-width: 399px;
        height: auto;
        opacity: 0.90;
    }

    #logo img {
        width: 100%;
        height: auto; 
        max-height: 60px;
        display: block;
    }


    h1 {
        font-family: TradeGothicBold;
        color: var(--brandWhite);
        font-size: 40px;
        text-decoration: underline;
        margin: 15px 15px;
    }


    p {
        font-family: RobotoRegular;
        color: var(--brandWhite);
    }

    #authors {
        font-size: .9rem;
        line-height: 1.2;
        text-align: left;
        margin: 15px;
    }

    .description {
        color: white;
        margin: 15px 15px;
        line-height: 1.3;
        font-size: .9rem;
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

    a:active {
        color: var(--brandMedGreen);
        
    }

    .location-label {
        display: block;
        margin: 15px 0 0 15px;
        color: white;
        font-family: RobotoRegular;
        font-size: 1rem;
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
        height: 25px;
        border: solid 1px var(--brandGray);
        border-radius: 5px;
        font-family: RobotoRegular;
        background-color: black;
        color: white;
        padding-left: 5px;
    }

    .dropdown-list {
        position: absolute;
        top: 40px;
        left: 0;
        right: 0;
        background-color: black;
        max-height: 200px;
        overflow-y: auto;
        z-index: 10;
    }

    .dropdown-item {
        padding: 3px;
        font-family: RobotoRegular;
        font-size: .8rem;
        cursor: pointer;
        color: white;
    }

    .dropdown-item:hover {
        background-color: var(--brandMedBlue);
    }

    .no-results {
        padding: 8px;
        color: gray;
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
        font-family: RobotoBold;
        margin-bottom: 5px;
        font-size: 1rem;
    }

    .gradient-bar {
        width: 100%;
        height: 20px;
        border: solid 1px var(--brandGray);
        border-radius: 5px;
        background: linear-gradient(90deg, rgba(0,0,0,1) 0%, rgba(30,55,101,1) 20%, rgba(0,127,163,1) 40%, rgba(101,177,199,1) 60%, rgba(111,199,234,1) 80%, rgba(255,255,255,1) 100%);
        margin-bottom: 5px;
    }

    .legend-label {
        display: flex; 
        justify-content: space-between;
        width: 100%;
        list-style: none;
        padding: 0;
        margin: 0;
        font-family: RobotoBold;
        font-size: 1rem;
        color: white;
    }
</style>