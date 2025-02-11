<script>
    export let metroRegionCentroids;
    export let searchQuery;
    export let dropdownOpen;
    export let selectLocation;
    export let handleInputChange;
    export let handleSearchInputClick;

    let filteredOptions = metroRegionCentroids.features;
    let selectedIndex = -1; // Track currently selected item
    let displayedOptions = []; // Track current options for navigation
    let isKeyboardSelection = false; // Track if last selection was from keyboard

    // Filter the options based on the search query
    $: filteredOptions = metroRegionCentroids.features.filter((feature) =>
        feature.properties.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Update displayed options when filter changes
    $: {
        displayedOptions = searchQuery === '' ? metroRegionCentroids.features : filteredOptions;
        // Reset selection when options change
        selectedIndex = -1;
    }

    function toggleDropdown(forcedState = null) {
        dropdownOpen = forcedState !== null ? forcedState : !dropdownOpen;
    }

    function handleKeydown(e) {
        if (!dropdownOpen && e.key !== 'Enter') return;

        switch(e.key) {
            case 'ArrowDown':
            case 'ArrowRight':
                e.preventDefault();
                isKeyboardSelection = true;
                selectedIndex = Math.min(selectedIndex + 1, displayedOptions.length - 1);
                break;
            case 'ArrowUp':
            case 'ArrowLeft':
                e.preventDefault();
                isKeyboardSelection = true;
                selectedIndex = Math.max(selectedIndex - 1, -1);
                break;
            case 'Enter':
                e.preventDefault();
                if (displayedOptions.length > 0) {
                    if (selectedIndex >= 0) {
                        selectLocation(displayedOptions[selectedIndex].properties.name);
                    } else {
                        selectLocation(displayedOptions[0].properties.name);
                    }
                    toggleDropdown(false);
                }
                break;
            case 'Escape':
                e.preventDefault();
                toggleDropdown(false);
                break;
        }
    }

    function handleMouseEnter(index) {
        if (!isKeyboardSelection) {
            selectedIndex = index;
        }
    }

    function handleMouseMove() {
        isKeyboardSelection = false;
    }

    function getHighlightedParts(text, query) {
        if (!query) return { before: text, match: '', after: '' };
        
        const lowerText = text.toLowerCase();
        const lowerQuery = query.toLowerCase();
        const index = lowerText.indexOf(lowerQuery);
        
        if (index === -1) return { before: text, match: '', after: '' };
        
        return {
            before: text.slice(0, index),
            match: text.slice(index, index + query.length),
            after: text.slice(index + query.length)
        };
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
        on:click={() => { if (!searchQuery) toggleDropdown(true); }}
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
        
        <svg 
            class="chevron {dropdownOpen ? 'open' : ''}" 
            width="12" 
            height="12" 
            viewBox="0 0 24 24"
            role="button"
            tabindex="0"
            aria-label="Toggle dropdown"
            on:click|stopPropagation={() => toggleDropdown()}
        >
            <path 
                fill="currentColor" 
                d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"
            />
        </svg>
    </div>

    {#if dropdownOpen}
        <div class="dropdown-list" role="listbox" tabindex="0" on:mousemove={handleMouseMove}>
            {#each displayedOptions as feature, i}
                {@const parts = getHighlightedParts(feature.properties.name, searchQuery)}
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <div
                    class="dropdown-item"
                    class:selected={i === selectedIndex}
                    role="option"
                    aria-selected={i === selectedIndex}
                    tabindex="0"
                    on:click={() => selectLocation(feature.properties.name)}
                    on:mouseenter={() => handleMouseEnter(i)}
                >
                    {parts.before}<span class="highlight">{parts.match}</span>{parts.after}
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
        position: relative;
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
        padding-right: 30px; /* Make room for chevron */
    }

    .chevron {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--brandGray);
        transition: transform 0.2s ease;
    }

    .chevron.open {
        transform: translateY(-50%) rotate(180deg);
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

    .dropdown-item.selected {
        background-color: var(--brandMedBlue);
    }

    .no-results {
        padding: 8px;
        color: gray;
    }

    .highlight {
        text-decoration: underline;
        font-weight: bold;
        color: var(--brandLightBlue);
    }
</style>
