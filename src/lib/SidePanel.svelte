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

    // Sort the features alphabetically by name
    metroRegionCentroids.features.sort((a, b) =>
        a.properties.name.localeCompare(b.properties.name)
    );

    function setMapDimensionView(dimension) {
        mapDimensionView = dimension;
    }
</script>

<div>
    <h1>Urban Activity Atlas</h1>
    <p id="authors">
        <a href='https://www.urbandisplacement.org/team/julia-greenberg/'>Julia Greenberg</a>, 
        <a href='https://www.linkedin.com/in/aniket-k-8a8b9921b/'>Aniket Kali</a>, 
        <a href='https://jamaps.github.io/'>Jeff Allen</a>, 
        <a href='https://karenchapple.com/'>Karen Chapple</a></p>
    <hr>
    <p class="description">
        Certain parts of cities tend to be more popular than others, as people might congregate around commercial districts, downtowns, major transit stations, and other key places. Using mobile location data, we created an atlas where you can see what parts of a city people spend their time in.
    </p> 
    <p class="description">
        Use this tool to explore how human activity levels vary geographically across a particular city, in a 300 largest metropolitan regions in the US and Canada.
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

    <p class="description">
        The part of the grid with a
        {mapDimensionView === "2D" 
            ? "brighter colour" 
            : "brighter colour and taller bar"
        }
        is where the most people stopped or visited between the year-long period of April 1, 2023 to March 31, 2024. 
    </p> 
    <p class="description">
        Activity level data shown is normalized by the total activity in each Metropolitan region. That is, activity within one region (eg. Toronto) is not currently comparable to another (eg. New York-Newark-Jersey City).
    </p>
    
    <div class="legend">
        <p class="legend-title">Activity Level (per region):</p>
        <div class="gradient-bar"></div>  
        <ul class="legend-label">
            <li class="low">Low</li>
            <li class="high">High</li>
        </ul>
    </div>

    <div class="button-container">
        <div id="2D" class={`button ${mapDimensionView === "2D" ? "selected" : "not-selected"}`} on:click={() => setMapDimensionView("2D")}>2D View</div>
        <div id="3D" class={`button ${mapDimensionView === "3D" ? "selected" : "not-selected"}`} on:click={() => setMapDimensionView("3D")}>3D View</div>
    </div>

    <hr>

    <p class="description">
        <i>The activity data on the map is derived from a sample of mobile phone data via <a href="https://spectus.ai/" target="_blank" rel="noopener noreferrer">Spectus</a>. Other reference data on the map are from <a href="https://www.openstreetmap.org/" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> via <a href="https://protomaps.com/" target="_blank" rel="noopener noreferrer">Protomaps</a>. Check out our <a href="https://github.com/schoolofcities/urban-activity-atlas/" target="_blank" rel="noopener noreferrer">Github</a> for more information about the data and methods.</i>
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


    .button-container {
        display: flex; 
        width: calc(100% - 20px);
        height: 100%; 
        margin: 5px;
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



</style>