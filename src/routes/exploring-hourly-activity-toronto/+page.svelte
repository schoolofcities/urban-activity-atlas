<script>

	import TopSofC from '$lib/TopSofC.svelte';
	import MapImageCycle from './lib/MapImageCycle.svelte';
	import LineChart from './lib/LineCharts.svelte';
    import '../../assets/global-styles.css';
	import topImage from './assets/top-image.png';

</script>


<svelte:head>

	<title>Activity Patterns Greater Toronto Area | School of Cities</title>

	<meta name="description" content="Exploring daily and hourly activity patterns in Toronto via charts and animated maps">
	<meta name="author" content="Cameron Kerr, Julia Greenberg, Jeff Allen">

	<meta property="og:title" content="Activity Patterns Greater Toronto Area | School of Cities" />
	<meta property="og:description" content="Exploring daily and hourly activity patterns in Toronto via charts and animated maps" />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://schoolofcities.github.io/urban-activity-atlas/exploring-hourly-activity-toronto" />
	<meta property="og:image" content="https://schoolofcities.github.io/urban-activity-atlas/web-card-gta-activity.png" />
	<meta property="og:locale" content="en_CA">

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://schoolofcities.github.io/urban-activity-atlas/exploring-hourly-activity-toronto" />
	<meta name="twitter:creator" content="@UofTCities" />
	<meta name="twitter:title" content="Activity Patterns Greater Toronto Area | School of Cities" />
	<meta name="twitter:description" content="Exploring daily and hourly activity patterns in Toronto via charts and animated maps" />
	<meta name="twitter:image" content="https://schoolofcities.github.io/urban-activity-atlas/web-card-gta-activity.png" /> 

</svelte:head>



<TopSofC/>

<main>

<div class="title">
	<img src={topImage} alt=""/>
    <h1>Exploring hourly activity patterns in Toronto</h1>
	<p id="authors">
		<a href="https://camhkerr.com/" target="_blank">Cameron Kerr</a>,
		<a href="https://www.urbandisplacement.org/team/julia-greenberg/" target="_blank">Julia Greenberg</a>,
		<a href="https://jamaps.github.io/" target="_blank">Jeff Allen</a> |
		June 2025
	</p>
</div>

<div class="text">
    <p>
		Metropolitan regions are constantly changing, complex systems. As their inhabitants and visitors commute between home and work, run errands, and engage in other activities, regions develop their own unique pulse and rhythm.	
	</p>
    <p>	
		The following visualizations illustrate this movement throughout the Greater Toronto Area (GTA)–a region with 
		almost 7 million people and a mix of urban, rural, and suburban communities–at different hours of the day using anonymized and aggregated data collected 
		from mobile devices.
	</p>
    <p>
		To do so, we selected over 16,000 grid cells, each about 1 kilometer wide, across the GTA. For each of these grid cells, we measured hourly activity by calculating the <i>accumulated time</i> that a sample of mobile devices (i.e., cell phones) spent in each grid 
		cell. For example, if two mobile devices each spent 30 minutes of a given hour in a given cell, the region would be assigned an accumulated time of 1 for that hour.
	</p>
	
	<p>
		We then mapped the results and calculated statistics summarizing the patterns that we observed. 
	</p>
	<p>
		The first map below shows the total accumulated time for each hour (shown using the 24 hour clock) of the average weekday and weekend in the summer of 2024 in the GTA. There isn't much fluctuation, demonstrating that the spatial distribution of total hourly activity is relatively constant. Activity at all hours during both types of days is consistently concentrated in specific locations (e.g. downtown Toronto)
	</p>
</div>



<MapImageCycle 
	title = "Mean hourly activity in Toronto"
	folder_weekday="exploring-hourly-activity-toronto/Weekday_Total_small"
	folder_weekend="exploring-hourly-activity-toronto/Weekend_Total_small"
	legendColors = {["#331d33","#c53e2e","#eddd53"]}
	legendLabels = {['Few active mobile devices','Many active mobile devices']}
/>

<div class="text">
    <p>	
		However, the map does reveal some interesting trends when looking closely. In the region overall, there is less activity at night.
		There is also a notable dark area on the map where the Pearson International Airport is located, indicating that there is
		generally less activity there compared to other parts of the region at night.
	</p>
</div>

<LineChart 
  path_to_data="exploring-hourly-activity-toronto/data/pings_normalized.csv" 
  title="Hourly activity in Toronto by day of the week" 
  yticks={[0.5, 0.75, 1, 1.25, 1.5]}
  y_axis_title="Mean normalized hourly activity"
/>

<div class="text">
	<p>
		The plot above shows the number of active devices in the sample during each hour throughout the week. The observed drop could be 
		due to the nature of the device location data, as lower overall levels of movement at night may result in fewer instances of devices' 
		locations being collected by the data provider. Another factor could be commuters coming into the GTA to work during the day and 
		leaving the region at night.
	</p>
	<p>
		In the map shown above, the underlying population density of the region distribution obscures hourly changes in activity. 
		In other words, since there are almost always more people in the city of Toronto (especially downtown) than anywhere else in the region, the spatial distribution of overall activity levels always looks fairly similar.
	</p>
	<p>
		To better illustrate <i>relative</i> changes in activity, the map below shows the difference between each individual cell's hourly 
		activity and its <i>average</i> hourly activity throughout the summer of 2024. This new metric
		measures how much more or less activity occurs in a given cell compared to the typical level of activity in that cell. 
	</p>
</div>

<MapImageCycle 
	title = "Mean-subtracted hourly activity in Toronto"
	folder_weekday="exploring-hourly-activity-toronto/Weekday_Difference_small"
	folder_weekend="exploring-hourly-activity-toronto/Weekend_Difference_small"
	legendColors = {["#d0f9ff","#4ca4c3","#331d33","#c53e2e","#eddd53"]}
	legendLabels = {['Relatively low activity', 'Mean activity', 'Relatively high activity']}
/>

<div class="text">
	<p>
		Patterns of movement throughout the region are much more pronounced in this version of the map. This map reveals that people cluster in employment centers during weekdays and then become more dispersed during weekday evenings. For example, the southeastern part of 
		Brampton and northeastern Mississauga is a massive employment area that becomes busier than usual during weekday working hours. During weekday evenings, on the other hand, the more residential northern and western parts of Brampton experience higher than average activity.
	</p>
	<p>		
		This trend of increased activity in employment zones during weekday working hours is prevalent throughout the GTA, including
		in the southern part of Vaughan, parts of Markham, and in downtown Toronto. Areas that mostly consist of residential buildings (rather than retail and commercial) have more activity in the evenings. Commuting patterns are also highlighted in the weekday version of the map, as activity visibly increases between 3 pm and 6 pm on Highway 400, Highway 401, and the QEW.
	</p>
	<p>
		Spatial patterns during the weekend are somewhat similar to weekday patterns, with some key differences. While weekday activity
		generally begins around 7 am, especially in the northwest part of the region and around the airport, on weekends
		there is still low overall activity at this time. Weekend activity picks up a few hours later, around 10 or 11 am.
	</p>
	<p>
		Activity during the day is also more evenly spread out throughout the region on weekends, and does not concentrate in major 
		employment areas like on weekdays. During both weekends and weekdays, however, activity in the central part of the city 
		of Toronto increases significantly around 10 or 11 pm.
	</p>
	<h2>Diversity and clustering</h2>
	<p>
		Diversity and clustering statistics were used to quantify the daily patterns observed in the maps above. <a href="https://en.wikipedia.org/wiki/Diversity_index#Shannon_index" target="_blank">Shannon's Diversity 
		Index</a> captures both <i>richness</i> (the number of grid cells on the map with activity) and <i>evenness</i> (how evenly that 
		activity is distributed among them). 
	</p>
	<p>		
		A high Shannon Index means that many cells have activity and that activity levels are relatively balanced across them. In contrast, a low Shannon Index suggests that fewer cells are experiencing activity and that activity is concentrated in specific cells. 
	</p>
	<p>
		Note that this index is "spatially unaware". In other words, if all the cells were shuffled into different positions on the map, the Shannon index value would remain the same.
	</p>
</div>

<LineChart 
	path_to_data="exploring-hourly-activity-toronto/data/shannon.csv" 
	title="Shannon diversity index of hourly activity in Toronto" 
	yticks={[7.9, 8, 8.1, 8.2]}
	y_axis_title=""
/>

<div class="text">
	<p>
		The plot above shows that activity becomes more <i>spatially diverse</i> during daytime hours, peaking between 3 pm and 5 pm, and then decreases in the evening and remains low throughout the night. Although differences in the actual index values are relatively small, an <a href="https://search.r-project.org/CRAN/refmans/ARTool/html/art.html" target="_blank">Aligned Rank Transform (ART) ANOVA</a> test confirmed that the variation in diversity between day and night is statistically 
		significant.
	</p>
	<p>		
		One possible explanation is that during the day, people are more mobile and spend less time staying fixed in specific locations
		relative to evenings, especially during commuting hours (when diversity peaks). The diversity index also increases slightly later in 
		the day on weekends compared to weekdays, likely corresponding with non-work weekend routines.
	</p>
	<p>
		As mentioned above, Shannon's Index reflects both <i>richness</i> and <i>evenness</i>. To better understand each component's 
		contribution to diversity, they were examined seperately. Richness, in this case, represents the number of cells in the GTA that 
		are visited within a given hour. Evenness indicates the degree to which activity is uniformly distributed throughout the region.
	</p>
</div>

<LineChart 
  path_to_data="exploring-hourly-activity-toronto/data/richness.csv" 
  title="Proportion of cells with activity throughout the day" 
  yticks={[0.4, 0.5, 0.6, 0.7]}
  y_axis_title="Richness"
/>

<div class="text">
	<p>
		Richness (the proportion of grid cells experiencing activity) reveals a pattern similar to Shannon's Diversity Index. During the day, more people are moving around, generating activity in a large number of cells. At night, activity becomes concentrated in 
		residential areas, leaving roughly half of the cells inactive.
	</p>
	<!-- <p>
		Additionally, the drop in the number of mobile devices, as seen in the first plot, contributes to a lower number of active cells. 
	</p> -->
</div>

<LineChart 
  path_to_data="exploring-hourly-activity-toronto/data/evenness.csv" 
  title="Evenness of activity throughout the day" 
  yticks={[0.86, 0.87, 0.88, 0.89, 0.9]}
  y_axis_title="Evenness"
/>

<div class="text">
	<p>
		Evenness (how evenly activity is spread out throughout the region) follows a reverse pattern. It generally 
		spikes at night around 3 am and gradually decreases during the day, likely reflecting the transition from home to more concentrated areas of work and leisure.
	</p>
	<p>
		Evenness also increases again slightly on weekdays between 3 pm and 5 pm, most likely a result of commuters spreading out throughout the GTA as they leave work.
	</p>
	<p>
		In addition to diversity indices, clustering was calculated using the <a href="https://en.wikipedia.org/wiki/Moran%27s_I" target="_blank">Moran's I</a> statistic for each hour throughout the week. A high, positive (between 0 and +1) Moran’s I value indicates that cells with similar activity are geographically close to each other, suggesting strong spatial autocorrelation. A value near zero suggests that activity levels are randomly distributed across space. A low negative value (between 0 and -1) indicates that high-activity cells are typically surrounded by low-activity cells and vice versa.
	</p>
</div>

<LineChart 
	path_to_data="exploring-hourly-activity-toronto/data/moran.csv" 
	title="Spatial clustering of hourly activity in Toronto" 
	yticks={[0.34, 0.38, 0.42, 0.46]}
	y_axis_title="Moran's I of hourly activity in Toronto"
/>

<div class="text">
	<p>
		The plot above reveals that activity is more spatially concentrated during the day, especially in late afternoons, compared to evenings and nights, when activity is more dispersed. This clustering trend is relatively similar to the trends for diversity and richness.
	</p>
	<p>			
		However, one noticeable difference is that the clustering plot shows a larger disparity between weekends and weekdays compared to the diversity and richness plots. On Saturdays and especially Sundays, there is less spatial clustering during the day compared to weekdays.
	</p>
	<p>			
		In other words, on weekend mornings and afternoons, there is a similar, even slightly higher proportion of grid cells with activity compared to weekday mornings and afternoons. However, the places where people spend time on weekend mornings and afternoons are less spatially concentrated. This makes sense, given that employment centers tend to be in specific areas whereas leisure activities are generally more spread out.
	</p>
</div>

<div class="text">

	<h2>
		Data sources:
	</h2>
	<p style="font-size: 15px;">
		Aggregated mobility data are provided by <a href="https://cuebiq.com/" target="_blank">Cuebiq</a>, a location intelligence platform. Data is collected from anonymized users who have opted-in to provide access to their location data anonymously, through a CCPA and GDPR-compliant framework. Through its Social Impact program, Cuebiq provides mobility insights for academic research and humanitarian initiatives. The Cuebiq responsible data sharing framework enables research partners to query anonymized and privacy enhanced data, by providing access to an auditable, on-premise Data Cleanroom environment. All final outputs provided to partners are aggregated in order to preserve privacy
	</p>
	<p style="font-size: 15px;">
		The frames of the animated maps were created using QGIS. They additionally include reference data (municipal boundaries) from Statistics Canada.
	</p>
	<p style="font-size: 15px;">
		More information about the data sources and related projects are available on <a href="https://github.io/schoolofcities/urban-activity-atlas/" target="_blank">GitHub</a>.
	</p>

</div>

</main>





<style>

	body {
		background-color: black;
	}

	main {
		background-color: #000000;
		margin-top: -150px;
		margin-bottom: -150px;
		padding-top: 150px;
		padding-bottom: 50px;
	}

    .title, .text {
        max-width: 640px;
		width: 100%;
		min-width: 350px;
        margin: 0 10px;
		color: white;
		margin: 0 auto;
    }

    .title {
		margin-top: 120px;
		margin-bottom: 25px;
		overflow-x: hidden;
	}

	.title img {
		max-width: 575px;
		width: 100%;
		padding: 20px;
	}
	
	h1 {
        margin: 0;
        padding-left: 20px;
		padding-right: 20px;
		font-size: 32px;
		font-family: TradeGothicBold, sans-serif;
		font-weight: normal;
    }

	h2 {
        margin: 0 auto;
		text-align: center;
        padding-left: 20px;
		padding-right: 20px;
		padding-top: 20px;
		font-family: TradeGothicBold, sans-serif;
		font-weight: normal;
		font-size: 26px;

    }

	h3 {
        margin: 0 auto;
		text-align: center;
        padding-left: 20px;
		padding-right: 20px;
		padding-top: 20px;
		font-family: TradeGothicBold, sans-serif;
		font-weight: normal;
		font-size: 20px;
    }

    p {
        margin: 10px 0;
        line-height: 1.5;
		font-size: 17px;
		padding-left: 20px;
		padding-right: 20px;
		font-family: RobotoRegular, sans-serif;
		font-weight: normal;
    }

	a {
		color: var(--brandLightBlue);
	}

	a:hover {
		color: var(--brandMedGreen);
	}

</style>