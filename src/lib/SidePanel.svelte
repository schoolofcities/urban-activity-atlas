<script>
    import logo from '../assets/top-logo-full.svg';
    import Dropdown from './Dropdown.svelte';

    // Props
    export let metroRegionCentroids;
    export let searchQuery;
    export let dropdownOpen;
    export let handleInputChange;
    export let handleSearchInputClick;
    export let selectLocation;
    export let mapDimensionView;
    export let timePeriod;
    export let changePeriodFrom;
    export let changePeriodTo;

    // Sort the features alphabetically by name
    metroRegionCentroids.features.sort((a, b) =>
        a.properties.name.localeCompare(b.properties.name)
    );

    // Pending states
    let pendingSingleTimePeriod = timePeriod !== "change" ? timePeriod : "2023-2024";
    let pendingChangePeriodFrom = changePeriodFrom;
    let pendingChangePeriodTo = changePeriodTo;

    function setMapDimensionView(dimension) {
        mapDimensionView = dimension;
    }

    function setPendingSingleTimePeriod(period) {
        pendingSingleTimePeriod = period;
    }

    function setPendingChangePeriodFrom(period) {
        pendingChangePeriodFrom = period;
        if (!period) {
            pendingChangePeriodTo = "";
            return;
        }

        if (period === "2023-2024" && pendingChangePeriodTo !== "2024-2025") {
            pendingChangePeriodTo = "";
        }
    }

    function setPendingChangePeriodTo(period) {
        pendingChangePeriodTo = period;
    }

    function getPeriodLabel(period) {
        if (period === "2019-2020") return "04/2019-03/2020";
        if (period === "2023-2024") return "04/2023-03/2024";
        if (period === "2024-2025") return "04/2024-03/2025";
        return "";
    }

    const changeFromOptions = [
        { value: "2019-2020", label: "04/2019-03/2020" },
        { value: "2023-2024", label: "04/2023-03/2024" }
    ];

    $: changeToOptions = pendingChangePeriodFrom === "2019-2020"
        ? [
            { value: "2023-2024", label: "04/2023-03/2024" },
            { value: "2024-2025", label: "04/2024-03/2025" }
        ]
        : pendingChangePeriodFrom === "2023-2024"
            ? [{ value: "2024-2025", label: "04/2024-03/2025" }]
            : [];

    let fromDropdownOpen = false;
    let toDropdownOpen = false;

    function toggleFromDropdown() {
        fromDropdownOpen = !fromDropdownOpen;
        if (fromDropdownOpen) toDropdownOpen = false;
    }

    function toggleToDropdown() {
        if (!pendingChangePeriodFrom) return;
        toDropdownOpen = !toDropdownOpen;
        if (toDropdownOpen) fromDropdownOpen = false;
    }

    function selectFromPeriod(period) {
        setPendingChangePeriodFrom(period);
        fromDropdownOpen = false;
        toDropdownOpen = false;
    }

    function selectToPeriod(period) {
        setPendingChangePeriodTo(period);
        toDropdownOpen = false;
    }

    function closePeriodDropdowns() {
        fromDropdownOpen = false;
        toDropdownOpen = false;
    }

    function applySingleTimePeriod() {
        timePeriod = pendingSingleTimePeriod;
        // Optionally clear change logic so they don't leak state unexpectedly
        // changePeriodFrom = ""; 
        // changePeriodTo = "";
    }

    function applyChangeTimePeriod() {
        if (pendingChangePeriodFrom && pendingChangePeriodTo) {
            timePeriod = "change";
            changePeriodFrom = pendingChangePeriodFrom;
            changePeriodTo = pendingChangePeriodTo;
        }
    }

    const timePeriodDateRanges = {
        "2019-2020": "April 1, 2019 – March 31, 2020",
        "2023-2024": "April 1, 2023 – March 31, 2024",
        "2024-2025": "April 1, 2024 – March 31, 2025"
    };

    $: hasSelectedChangePeriods = Boolean(changePeriodFrom) && Boolean(changePeriodTo);
    $: changeRangeLabel = hasSelectedChangePeriods
        ? `${timePeriodDateRanges[changePeriodFrom]} and ${timePeriodDateRanges[changePeriodTo]}`
        : "selected windows";

    // Use applied timePeriod for text
    $: timePeriodRange = timePeriod === "change"
        ? changeRangeLabel
        : (timePeriodDateRanges[timePeriod] ?? timePeriodDateRanges["2023-2024"]);

    // The legend reflects the applied state
    $: isAppliedChangeMode = timePeriod === "change";
    $: legendTitle = isAppliedChangeMode
        ? `Change in activity`
        : "Activity level (per region):";
    $: legendLowLabel = isAppliedChangeMode ? `Decrease` : "Low";
    $: legendHighLabel = isAppliedChangeMode ? `Increase` : "High";

    const CHANGE_GRADIENT_COLORS = {
        start: "#ff9aa0",
        midDarkRed: "#8f232c",
        midpoint: "#000000",
        midDarkBlue: "#245e86",
        end: "#6fc7ea"
    };

    const ACTIVITY_GRADIENT_COLORS = {
        start: "#000000",
        navy: "#1e3765",
        teal: "#007fa3",
        lightBlue: "#65b1c7",
        skyBlue: "#6fc7ea",
        end: "#ffffff"
    };

    $: legendGradient = isAppliedChangeMode
        ? `linear-gradient(90deg, ${CHANGE_GRADIENT_COLORS.start} 0%, ${CHANGE_GRADIENT_COLORS.midDarkRed} 45%, ${CHANGE_GRADIENT_COLORS.midpoint} 50%, ${CHANGE_GRADIENT_COLORS.midDarkBlue} 55%, ${CHANGE_GRADIENT_COLORS.end} 100%)`
        : `linear-gradient(90deg, ${ACTIVITY_GRADIENT_COLORS.start} 0%, ${ACTIVITY_GRADIENT_COLORS.navy} 20%, ${ACTIVITY_GRADIENT_COLORS.teal} 40%, ${ACTIVITY_GRADIENT_COLORS.lightBlue} 60%, ${ACTIVITY_GRADIENT_COLORS.skyBlue} 80%, ${ACTIVITY_GRADIENT_COLORS.end} 100%)`;
</script>

<svelte:window on:click={closePeriodDropdowns} />

<div>

    <h1>Urban Activity Atlas</h1>
    <p id="authors">
        <a href='https://www.urbandisplacement.org/team/julia-greenberg/'>Julia Greenberg</a>, 
        <a href='https://www.linkedin.com/in/aniket-k-8a8b9921b/'>Aniket Kali</a>, 
        <a href='https://jamaps.github.io/'>Jeff Allen</a>, 
        <a href='https://karenchapple.com/'>Karen Chapple</a>,
        <a href='https://www.linkedin.com/in/yihoi-jung-0b95351b5/'>Yihoi Jung</a></p>
    <hr>
    <p class="description">
        This map shows which places people visit or spend time in the 300 largest metropolitan regions (by population) in the US and Canada. Choose a metro region by clicking on it on the map, or choosing from the dropdown below.
    </p>

    <!-- <p class="location-label">Select a metropolitan region:</p> -->
    <Dropdown
        {metroRegionCentroids}
        bind:searchQuery
        bind:dropdownOpen
        {selectLocation}
        {handleInputChange}
        {handleSearchInputClick}
    />

    <div class="button-container">
        <button type="button" class={`button ${searchQuery === '' ? "not-selected" : "selected"}`} on:click={() => selectLocation('')}>Clear selection</button>
    </div>

    <p class="description">
        The area with the
        {mapDimensionView === "2D" 
            ? "brightest white colour" 
            : "brightest white colour and tallest bar"
        }
        had the most visits in the selected metro region for the period between {timePeriodRange}.
    </p> 
    <p class="description">
        Activity level data shown is standardized by the total activity in each metropolitan region. Values are thus not comparable between regions since regions vary in size and population.
    </p>
    
    

    <div class="section">
        <p class="section-title">Time Period</p>
        <div class="button-container">
            <button type="button" class={`button period-button ${pendingSingleTimePeriod === "2019-2020" ? "selected" : "not-selected"}`} on:click={() => setPendingSingleTimePeriod("2019-2020")}>04/2019-03/2020</button>
            <button type="button" class={`button period-button ${pendingSingleTimePeriod === "2023-2024" ? "selected" : "not-selected"}`} on:click={() => setPendingSingleTimePeriod("2023-2024")}>04/2023-03/2024</button>
            <button type="button" class={`button period-button ${pendingSingleTimePeriod === "2024-2025" ? "selected" : "not-selected"}`} on:click={() => setPendingSingleTimePeriod("2024-2025")}>04/2024-03/2025</button>
        </div>
        <div class="apply-container" style="margin-top: 0px;">
            <button type="button" class="button apply-button" on:click={applySingleTimePeriod}>Apply</button>
        </div>
    </div>

    <div class="section">
        <p class="section-title">Change between time periods</p>
        <div class="change-row">
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <div class="period-dropdown-container" on:click|stopPropagation>
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <div
                    class="period-dropdown-toggle"
                    role="button"
                    tabindex="0"
                    aria-haspopup="listbox"
                    aria-expanded={fromDropdownOpen}
                    on:click={toggleFromDropdown}
                >
                    <div class="period-display {pendingChangePeriodFrom ? '' : 'placeholder'}">
                        {pendingChangePeriodFrom ? getPeriodLabel(pendingChangePeriodFrom) : 'Select start year'}
                    </div>
                    <svg
                        class="period-chevron {fromDropdownOpen ? 'open' : ''}"
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                    >
                        <path
                            fill="currentColor"
                            d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"
                        />
                    </svg>
                </div>

                {#if fromDropdownOpen}
                    <div class="period-dropdown-list" role="listbox">
                        {#each changeFromOptions as option}
                            <!-- svelte-ignore a11y_click_events_have_key_events -->
                            <div
                                class="period-dropdown-item"
                                class:selected={option.value === pendingChangePeriodFrom}
                                role="option"
                                aria-selected={option.value === pendingChangePeriodFrom}
                                tabindex="0"
                                on:click={() => selectFromPeriod(option.value)}
                            >
                                {option.label}
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>

            <span class="vs-label">vs.</span>

            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <div class="period-dropdown-container" on:click|stopPropagation>
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <div
                    class="period-dropdown-toggle {pendingChangePeriodFrom ? '' : 'disabled'}"
                    role="button"
                    tabindex="0"
                    aria-haspopup="listbox"
                    aria-expanded={toDropdownOpen}
                    aria-disabled={!pendingChangePeriodFrom}
                    on:click={toggleToDropdown}
                >
                    <div class="period-display {pendingChangePeriodTo ? '' : 'placeholder'}">
                        {pendingChangePeriodTo ? getPeriodLabel(pendingChangePeriodTo) : 'Select end year'}
                    </div>
                    <svg
                        class="period-chevron {toDropdownOpen ? 'open' : ''}"
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                    >
                        <path
                            fill="currentColor"
                            d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"
                        />
                    </svg>
                </div>

                {#if toDropdownOpen}
                    <div class="period-dropdown-list" role="listbox">
                        {#each changeToOptions as option}
                            <!-- svelte-ignore a11y_click_events_have_key_events -->
                            <div
                                class="period-dropdown-item"
                                class:selected={option.value === pendingChangePeriodTo}
                                role="option"
                                aria-selected={option.value === pendingChangePeriodTo}
                                tabindex="0"
                                on:click={() => selectToPeriod(option.value)}
                            >
                                {option.label}
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
        <div class="apply-container">
            <button type="button" class="button apply-button" on:click={applyChangeTimePeriod}>Apply</button>
        </div>
    </div>

    <div class="legend">
        <p class="legend-title">{legendTitle}</p>
        <div class="gradient-bar" style={`background: ${legendGradient};`}></div>
        <ul class="legend-label">
            <li class="low">{legendLowLabel}</li>
            <li class="high">{legendHighLabel}</li>
        </ul>
    </div>
    

    <div class="section">
        <p class="section-title">Map View:</p>
        <div class="button-container">
            <button type="button" id="2D" class={`button ${mapDimensionView === "2D" ? "selected" : "not-selected"}`} on:click={() => setMapDimensionView("2D")}>2D View</button>
            <button type="button" id="3D" class={`button ${mapDimensionView === "3D" ? "selected" : "not-selected"}`} on:click={() => setMapDimensionView("3D")}>3D View</button>
        </div>
    </div>

    <hr>

    <p class="description">
        <i>The activity data on the map is derived from a sample of mobile phone data via <a href="https://cuebiq.com/" target="_blank" rel="noopener noreferrer">Cuebiq</a>. Other reference data on the map are from <a href="https://www.openstreetmap.org/" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> via <a href="https://protomaps.com/" target="_blank" rel="noopener noreferrer">Protomaps</a>. Check out our <a href="https://github.com/schoolofcities/urban-activity-atlas/" target="_blank" rel="noopener noreferrer">Github</a> for more information about the data and methods.</i>
        <br><br>
        <i>Note: <a href="https://olis.oregonlegislature.gov/liz/2025R1/Measures/Overview/HB2008" target="_blank" rel="noopener noreferrer">Oregon's Consumer Privacy Act</a> enacted in 2025 prevents the collection of Cuebiq data, hence why Oregon could not be included.</i>
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
        opacity: 1;
    }

    #logo img {
        width: 100%;
        height: auto; 
        max-height: 60px;
        display: block;
    }

    #logo:hover {
        opacity: 0.75;
    }


    h1 {
        font-family: TradeGothicBold;
        color: var(--brandWhite);
        font-size: 2.2rem;
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

    .legend {
        list-style: none;
        padding: 0;
        margin: 0 20px 15px 15px;
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

    .section {
        margin-bottom: 15px;
    }

    .section-title {
        font-family: RobotoBold;
        margin-bottom: 0;
        margin-top: 0;
        margin-left: 15px;
        margin-right: 15px;
        font-size: 1rem;
    }

    .gradient-bar {
        width: calc(100% - 2px);
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
        font-family: RobotoItalic;
        font-size: 1rem;
        color: white;
    }

    .button-container {
        display: flex; 
        width: calc(100% - 20px);
        height: 100%; 
        margin: 5px;
        flex-wrap: wrap;
    }

    .button {
        flex: 1; 
        display: flex; 
        justify-content: center;
        align-items: center;
        font-size: 16px;
        font-weight: bold;
        color: white;
        background-color: var(--brandDarkBlue); 
        border: 1px solid var(--brandGray); 
        border-radius: 5px;
        cursor: pointer; 
        margin: 5px;
        padding: 5px;
        margin-left: 10px;
        transition: background-color 0.2s ease; 
    }

    .button.not-selected {
        opacity: 0.5;
    }


    .button:hover {
        background-color: var(--brandLightBlue); 
        opacity: 1;
    }

    .period-button {
        font-size: 14px;          
        padding: 4px 5px; /* smaller spacing */
        margin-right: 5px;
        margin-left: 10px;
    }

    .mode-inactive {
        opacity: 0.5;
    }

    .change-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 8px 20px 0 15px;
    }

    .period-dropdown-container {
        position: relative;
        flex: 1;
        min-width: 120px;
    }

    .period-dropdown-toggle {
        position: relative;
        display: flex;
        align-items: center;
        width: 100%;
        min-height: 38px;
        border: solid 1px var(--brandGray);
        border-radius: 5px;
        background-color: var(--brandDarkBlue);
        color: white;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }

    .period-dropdown-toggle:hover {
        background-color: var(--brandLightBlue);
    }

    .period-dropdown-toggle.disabled,
    .period-dropdown-toggle.disabled:hover {
        opacity: 0.5;
        cursor: not-allowed;
        background-color: var(--brandDarkBlue);
    }

    .period-display {
        width: 100%;
        font-family: inherit;
        font-size: 14px;
        font-weight: bold;
        color: white;
        padding: 6px 30px 6px 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .period-display.placeholder {
        color: rgba(255, 255, 255, 0.85);
    }

    .period-chevron {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--brandGray);
        transition: transform 0.2s ease;
        pointer-events: none;
    }

    .period-chevron.open {
        transform: translateY(-50%) rotate(180deg);
    }

    .period-dropdown-list {
        position: absolute;
        top: calc(100% + 2px);
        left: 0;
        right: 0;
        background-color: var(--brandDarkBlue);
        border: solid 1px var(--brandGray);
        border-radius: 5px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 20;
    }

    .period-dropdown-item {
        padding: 6px 8px;
        font-family: RobotoBold;
        font-size: .95rem;
        cursor: pointer;
        color: white;
    }

    .period-dropdown-item:hover,
    .period-dropdown-item.selected {
        background-color: var(--brandMedBlue);
    }

    .vs-label {
        color: var(--brandWhite);
        font-family: RobotoBold;
        font-size: 16px;
        white-space: nowrap;
    }

    .apply-container {
        display: flex;
        justify-content: flex-end;
        margin-right: 20px;
        margin-top: 10px;
    }

    .apply-button {
        font-size: 13px;
        padding: 5px 20px;
        margin: 0;
        flex: none;
    }

</style>