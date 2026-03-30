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

    function setMapDimensionView(dimension) {
        mapDimensionView = dimension;
    }

    function setTimePeriod(period) {
        timePeriod = period;
    }

    function updateChangeModeIfReady() {
        const hasValidSelection = Boolean(changePeriodFrom) && Boolean(changePeriodTo);
        if (hasValidSelection) {
            timePeriod = "change";
        }
    }

    function setChangePeriodFrom(period) {
        changePeriodFrom = period;
        if (!period) {
            changePeriodTo = "";
            return;
        }

        if (period === "2023-2024" && changePeriodTo !== "2024-2025") {
            changePeriodTo = "";
        }

        updateChangeModeIfReady();
    }

    function setChangePeriodTo(period) {
        changePeriodTo = period;
        updateChangeModeIfReady();
    }

    const timePeriodRanges = {
        "2019-2020": "April 1, 2019 and March 31, 2020",
        "2023-2024": "April 1, 2023 and March 31, 2024",
        "2024-2025": "April 1, 2024 and March 31, 2025",
        "change": "the difference between selected windows"
    };

    $: hasSelectedChangePeriods = Boolean(changePeriodFrom) && Boolean(changePeriodTo);
    $: changeRangeLabel = hasSelectedChangePeriods
        ? `the difference between ${changePeriodFrom} and ${changePeriodTo}`
        : "the difference between selected windows";
    $: timePeriodRanges.change = changeRangeLabel;

    $: timePeriodRange = timePeriodRanges[timePeriod] ?? timePeriodRanges["2023-2024"];
    $: isChangeMode = timePeriod === "change";
    $: legendTitle = isChangeMode
        ? `Change in activity`
        : "Activity level (per region):";
    $: legendLowLabel = isChangeMode ? `Decrease` : "Low";
    $: legendHighLabel = isChangeMode ? `Increase` : "High";

    const CHANGE_GRADIENT_COLORS = {
        start: "#ff472f",
        midDarkRed: "#ff472fae",
        midpoint: "#00000089",
        midDarkBlue: "#78d9ffae",
        end: "#78d9ff"
    };

    const ACTIVITY_GRADIENT_COLORS = {
        start: "#000000",
        navy: "#1e3765",
        teal: "#007fa3",
        lightBlue: "#65b1c7",
        skyBlue: "#6fc7ea",
        end: "#ffffff"
    };

    $: legendGradient = isChangeMode
        ? `linear-gradient(90deg, ${CHANGE_GRADIENT_COLORS.start} 0%, ${CHANGE_GRADIENT_COLORS.midDarkRed} 25%, ${CHANGE_GRADIENT_COLORS.midpoint} 50%, ${CHANGE_GRADIENT_COLORS.midDarkBlue} 75%, ${CHANGE_GRADIENT_COLORS.end} 100%)`
        : `linear-gradient(90deg, ${ACTIVITY_GRADIENT_COLORS.start} 0%, ${ACTIVITY_GRADIENT_COLORS.navy} 20%, ${ACTIVITY_GRADIENT_COLORS.teal} 40%, ${ACTIVITY_GRADIENT_COLORS.lightBlue} 60%, ${ACTIVITY_GRADIENT_COLORS.skyBlue} 80%, ${ACTIVITY_GRADIENT_COLORS.end} 100%)`;
</script>

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
            ? "brightest white color" 
            : "brightest white color and tallest bar"
        }
        had the most visits of anywhere in the selected metro region in the period between {timePeriodRange}.
    </p> 
    <p class="description">
        Activity level data shown is standardized by the total activity in each metropolitan region. Values are thus not comparable between regions since regions vary in size and population.
    </p>
    
    

    <div class="section">
        <p class="section-title">Time Period</p>
        <div class={`button-container ${isChangeMode ? "mode-inactive" : ""}`}>
            <button type="button" class={`button period-button ${timePeriod === "2019-2020" ? "selected" : "not-selected"}`} on:click={() => setTimePeriod("2019-2020")}>04/2019-03/2020</button>
            <button type="button" class={`button period-button ${timePeriod === "2023-2024" ? "selected" : "not-selected"}`} on:click={() => setTimePeriod("2023-2024")}>04/2023-03/2024</button>
            <button type="button" class={`button period-button ${timePeriod === "2024-2025" ? "selected" : "not-selected"}`} on:click={() => setTimePeriod("2024-2025")}>04/2024-03/2025</button>
        </div>
        <!-- <p class="description" style="margin-top: -0px;">Time period is from {timePeriodRange}</p> -->
    </div>

    <div class = {`section ${!isChangeMode ? "mode-inactive" : ""}`}>
        <p class = "section-title">Change between time periods</p>
        <div class = "change-row">
            <select class = "period-select" value = {changePeriodFrom} 
            on:change={(e) => setChangePeriodFrom(e.currentTarget.value)}>
                <option value = "">Select start year</option>
                <option value = "2019-2020">04/2019-03/2020</option>
                <option value = "2023-2024">04/2023-03/2024</option>
            </select>
            <span class = "vs-label">vs.</span>
            <select class = "period-select" value = {changePeriodTo} 
            disabled={!changePeriodFrom}
            on:change={(e) => setChangePeriodTo(e.currentTarget.value)}>
                <option value = "">Select end year</option>
                {#if changePeriodFrom === "2019-2020"}
                    <option value="2023-2024">04/2023-03/2024</option>
                {/if}
                <option value="2024-2025">04/2024-03/2025</option>
            </select>
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
        padding: 4px 8px; /* smaller spacing */
        margin: 3px; /* smaller gap */
        margin-left: 5px;
    }

    .mode-inactive {
        opacity: 0.5;
    }

    .change-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 8px 15px 0 15px;
    }

    .period-select {
        flex: 1;
        min-width: 0;
        height: 38px;
        border-radius: 5px;
        border: 1px solid var(--brandGray);
        background-color: var(--brandDarkBlue);
        color: var(--brandWhite);
        cursor: pointer; 
        font-size: 12px;
        font-weight: bold;
        padding: 0 10px;
        transition: background-color 0.2s ease; 
    }

    .period-select:hover {
        background-color: var(--brandLightBlue);
        opacity: 1;
    }

    .vs-label {
        color: var(--brandWhite);
        font-family: RobotoBold;
        font-size: 0.95rem;
        white-space: nowrap;
    }



</style>