<script>
    export let metroRegionCentroids;
    export let searchQuery;
    export let dropdownOpen;
    export let selectLocation;
    export let handleInputChange;
    export let handleSearchInputClick;

    let filteredOptions = metroRegionCentroids.features;

    // Filter the options based on the search query
    $: filteredOptions = metroRegionCentroids.features.filter((feature) =>
        feature.properties.name.toLowerCase().startsWith(searchQuery.toLowerCase())
    );

    function handleKeydown(e) {
        if (e.key === 'Enter' && filteredOptions.length > 0) {
            e.preventDefault();
            selectLocation(filteredOptions[0].properties.name);
            dropdownOpen = false;
        }
    }
</script>

<div class="dropdown-container">
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <div
        class="dropdown-toggle"
        role="button"
        tabindex="0"
        aria-haspopup="listbox"
        aria-expanded={dropdownOpen}
        on:click={() => { if (!searchQuery) dropdownOpen = true; }}
    >
        <input
            type="text"
            class="search-input"
            bind:value={searchQuery}
            placeholder={searchQuery ? '' : 'Search metropolitan region...'}
            on:input={handleInputChange}
            on:click={handleSearchInputClick}
            on:keydown={handleKeydown}
        />
    </div>

    {#if dropdownOpen}
        <div class="dropdown-list" role="listbox">
            {#each searchQuery === '' ? metroRegionCentroids.features : filteredOptions as feature}
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <div
                    class="dropdown-item"
                    role="option"
                    aria-selected="false"
                    tabindex="0"
                    on:click={() => selectLocation(feature.properties.name)}
                >
                    {feature.properties.name}
                </div>
            {:else}
                <div class="no-results">No results found</div>
            {/each}
        </div>
    {/if}
</div>

<style>
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
</style>
