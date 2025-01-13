<script>
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

<style>
    .panel {
        width: 350px;
        position: absolute;
        background-color: #1f1f1f;
        z-index: 1;
    }

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

    a {
        color: #fffb85;
        text-decoration: none;
        font-family: RobotoRegular;
    }

    a:visited {
        color: #fffb85;
        font-family: RobotoRegular;
    }

    a:hover {
        color: #70a863;
        text-decoration: underline;
        font-family: RobotoRegular;
    }

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
</style>