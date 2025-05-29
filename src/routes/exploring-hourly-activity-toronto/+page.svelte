<script>

	import TopSofC from '$lib/TopSofC.svelte';
	import MapImageCycle from './lib/MapImageCycle.svelte';
	import LineChart from './lib/LineCharts.svelte';
    import '../../assets/global-styles.css';
	import topImage from './assets/top-image.png';

</script>


<TopSofC/>

<main>

<div class="title">
	<img src={topImage} alt=""/>
    <h1>Exploring hourly activity patterns in Toronto</h1>
	<p id="authors">
		<a href="https://camhkerr.com/">Cameron Kerr</a>,
		<a href="https://www.urbandisplacement.org/team/julia-greenberg/">Julia Greenberg</a>,
		<a href="https://jamaps.github.io/">Jeff Allen</a>
	</p>
</div>

<div class="text">
    <p>
		Metropolitan regions are constantly changing, complex systems. As their inhabitants and visitors move between 
		home and work, to and from events, and through their daily routines, regions develop their own unique pulse.	
	</p>
    <p>	
		The following visualizations illustrate this movement through the Greater Toronto Area (GTA) - a region with 
		almost 7 million people and a mix of urban, rural, and suburban communities - at different hours of the day using mobile 
		phone data.
	</p>
	<h2>Methodology</h2>
    <p>
		The bounding box around the GTA (i.e., the rectangular area containing the region's boundaries) was subdivided into a 
		rectangular grid containing over 16,000 grid cells, each about 1 kilometer wide.
	</p>
	<p>Hourly activity was measured using the <i>accumulated time</i> in each grid cell. For example, if two mobile 
		devices each spend 30 minutes of a given hour in a given cell, the region has an accumulated time of 1 in that hour. The time 
		each device spends in each cell was calculated using a sample of mobile location data provided by <a href="https://docs.spectus.ai/" target="_blank">Spectus</a>.
	</p>
</div>

<MapImageCycle 
	title = "Mean hourly activity in Toronto"
	folder_weekday="exploring-hourly-activity-toronto/Weekday_Total_small"
	folder_weekend="exploring-hourly-activity-toronto/Weekend_Total_small"
	legendColors = {["#331d33","#c53e2e","#eddd53"]}
	legendLabels = {['Few active mobile phones','Many active mobile phones']}
/>

<div class="text">
	<p>
		The map above, which shows the total accumulated time for the average weekday and weekend in the summer of 2024 in the GTA,
		demonstrates that the spatial distribution of total hourly activity is relatively constant. Despite some small fluctuations, 
		activity at all hours during both types of days is consistently concentrated in the city of Toronto, especially downtown.
	</p>
    <p>	
		However, the map does reveal some interesting trends. In the region overall, there is less activity in general at night.
		There is also a notable dark area on the map where the Pearson International Airport is located, indicating that there is
		generally less activity there compared to other parts of the region.
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
		The plot above shows the number of active phones in the sample during each hour throughout the week. The observed drop could be 
		due to the nature of the mobile location data, as lower overall levels of movement at night results in fewer cell phone "pings". 
		Another factor could be commuters coming into the GTA to work during the day and leaving the region at night.
	</p>
	<p>
		In the first map shown above, the underlying population density of the region distribution obscures hourly changes in activity. 
		In other words, since there are almost always more people downtown and in the city of Toronto than anywhere else in the region,
		the spatial distribution of overall activity levels always looks pretty similar.
	</p>
	<p>
		To better visualize <i>relative</i> changes in activity, we calculated the difference between each individual cell's hourly 
		activity and its <i>average</i> hourly activity throughout the summer of 2024. This new metric - shown in the map below - 
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
		Patterns of movement throughout the region are much more pronounced in this version of the map. Similar to the previous map, most 
		cells in this map experience lower-than-average activity at night and higher-than-average activity during the day. This map also 
		shows, however, how people cluster in employment centers during weekdays and then become more dispersed during weeknights.

		HERE ONWARD IS WHERE I NEED TO KEEP EDITING!

		For example, the southeastern part of Brampton is an employment area that becomes busier during weekdays, with the surrounding 
		northern and western part containing residential areas. During the evening, these residential areas have a higher than average activity and during 9-5 on weekdays the employment areas are at higher activity. Similarly, Vaughan's primary employment area is located in the South and is surrounded by residential areas. Activity is concentrated in the employment areas during 9-5 on weekdays and spreads out to the surrounding areas in the evening. Due to it's high density it is difficult to discern similar patterns for Toronto, but a signfiicant increase in activity can be seen in the downtown core during working hours. Additionally, between 3 pm and 6 pm lines of increased activity can be seen on highway 400 and highway 401, representing the commute out of commercial areas.
	</p>
</div>

<div class="text">
	<p>
		This map demonstrates both large and small scale flucuations throughout the day. Similar to the previous map, most cells have a lower than average activity during the night and higher than average activity during the day. In addition, we can see movement from residential areas and into employment areas during the day. For example, the south-eastern part of Brampton is an employment area with the surrounding northern and western part containing residential areas. During the evening, these residential areas have a higher than average activity and during 9-5 on weekdays the employment areas are at higher activity. Similarly, Vaughan's primary employment area is located in the South and is surrounded by residential areas. Activity is concentrated in the employment areas during 9-5 on weekdays and spreads out to the surrounding areas in the evening. Due to it's high density it is difficult to discern similar patterns for Toronto, but a signfiicant increase in activity can be seen in the downtown core during working hours. Additionally, between 3 pm and 6 pm lines of increased activity can be seen on highway 400 and highway 401, representing the commute out of commercial areas.
	</p>
	<p>
		In contrast to the commercial shift on weekdays, the progression through a weekend is less predicatable. In the evening the distribution is similar to that seen on weekdays, with most high activity occuring in residential areas. However, activity during the day is scattered throughout commercial and residential areas. The activity also starts much later in the day, with low activity in central areas as late as 11 am. 
	</p>
	<h2>Diversity and clustering</h2>
	<p>
		Diversity and clustering statistics were used to quantify the daily patterns observed in the maps above. To measure the diversity of hourly activity across the GTA, we applied Shannon's Diversity Index. This index captures both the number of cells with activity (richness) and how evenly that activity is distributed among them (evenness). A high Shannon index means that many cells have activity and that activity levels are relatively balanced across them. In contrast, a low Shannon index suggests that fewer cells are active and that activity is concentrated in specific cells. Note that this index is spatially unaware, if all the cells were shuffled into different positions on the map, the Shannon index value would remain the same. 
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
		In the plot above a clear 'pulse' in diversity forms throughout the day. Activity becomes more diverse during daytime hours, with an additional spike between 3 pm and 5 pm. The diversity subsequently drops off in the evening and overnight. Although the differences in the actual index values are relatively small, an Aligned Rank Transform (ART) ANOVA test confirmed that the variation in diversity between day and night is statistically significant. One possible explanation is that during the day people are more mobile and are accumulating less activity in specific cells, especially during commuting hours (when diversity peaks). Additionally, this diversity pulse appears later in the day on Saturdays and Sundays, likely due to delayed daily routines on weekends. 
	</p>
	<p>
		As mentioned above, Shannon's index reflects both richness and evenness. To better understand each components contribution to diversity, we can examine them seperately. In our case, richness represents the number of cells in the GTA which are visited within a given hour. Evenness represents the degree to which activity is uniformly distributed. 
	</p>
</div>

<LineChart 
  path_to_data="exploring-hourly-activity-toronto/data/richness.csv" 
  title="Fraction of cells with activity throughout the day" 
  yticks={[0.4, 0.5, 0.6, 0.7]}
  y_axis_title="Richness"
/>

<LineChart 
  path_to_data="exploring-hourly-activity-toronto/data/evenness.csv" 
  title="Evenness of activity throughout the day" 
  yticks={[0.86, 0.87, 0.88, 0.89, 0.9]}
  y_axis_title="Evenness"
/>

<div class="text">
	<p>
		The plot of richness (expressed here as the fraction of active cells) reveals a simlair daily 'pulse' to that seen in Shannon's diversity. During the day, more people are moving which generates activity in a large number of cells. At night, activity becomes concentrated in residential areas leaving roughly half of the cells inactive. Additionally, the drop in the number of phones (as seen in the first plot) contributes to a lower number of active cells. 
	</p>
	<p>
		Evenness follows a different pattern; it tends to spike at night and gradually decreases during the day, with a smaller increase on weekdays between 3pm and 5 pm. The nightime spike likely results from low activity levels where urban and rural cells experience minimal activity. The increase between 3 and 5 pm may reflect commuting, as people spread out more evenly across the GTA. Note that despite the distinct pattern seen, the numerical change in evenness is small.
	</p>
	<p>
		To investigate clustering, we calculated Moran's I for each hour throughout the week. In our case, Moran's I measures whether cells with similar activity levels tend to be located near each other. A high Moran's I value indicates that cells with similar activity are spatially close, suggesting strong spatial autocorrelation. A value near zero suggests that activity levels are randomly distributed across space. A negative value indicates that high-activity cells are typically surrounded by low-activity cells and vice versa. Moran's I ranges from -1 (negative spatial autocorrelation) to +1 (positive spatial autocorrelation).
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
		Clustering patterns also exhibit a noticeable 'pulse' throughout the day. Between 10am and 5pm high levels of activity become more spatially concentrated. In the evening and overnight hours, this clustering diminishes and activity becomes more spatially dispersed. This pattern likely reflects the daily movement of people into concentrated employment or commercial areas during working hours, as reported in the maps above. Additionally, clustering is generally lower on weekends, particularly on Sundays. This supports our earlier observation in the maps that weekend activity lacks the structured, location-specific patterns which are observed during weekdays. 
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