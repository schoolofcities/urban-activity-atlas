<script>

	import TopSofC from '$lib/TopSofC.svelte';
	import MapImageCycle from './lib/MapImageCycle.svelte';
    import '../../assets/global-styles.css';

</script>


<TopSofC/>

<main>

<div class="title">
    <h1>Exploring hourly activity patterns in Toronto</h1>
	<p id="authors">
		<a href="https://camhkerr.com/">Cameron Kerr</a>
		<a href="https://www.urbandisplacement.org/team/julia-greenberg/">Julia Greenberg</a>
		<a href="https://jamaps.github.io/">Jeff Allen</a>
	</p>
</div>

<div class="text">
    <p>
		A city is a constantly changing complex system. Even hourly, as millions of people move from home to work, to events, and through their daily routines the city develops it's own pulse. We set out to visualize the pulse of the city and identify any patterns that emerge.
	</p>
    <p>
		The Greater Toronto Area (GTA) provides a model area to investigate as it contains almost 7 million people and a diverse set of rural, mid-size-and mega- cities. 
	</p>
    <p>
		The bounding box around the GTA was subdivided into a rectangular grid containing over 16,000 cells each about 1km wide. To investigate hourly activity across the GTA the accumulated time in each of these cells was calculated. Hourly activity was measured by the accumulated time in each cell (i.e if 2 people spend half of the hour in a given cell, the region has an accumulated time of 1 in that hour). The time each person spends in each cell was calculated using a sample of mobile location data provided by Spectus. In the map below the total accumulated time is shown for the average weekday and weekend over the summer of 2024 in the GTA.
	</p>
</div>

<MapImageCycle 
	title = "Hourly activity in Toronto via mobile phone data"
	folder_weekday="exploring-daily-activity-toronto/Weekday_Total_small"
	folder_weekend="exploring-daily-activity-toronto/Weekend_Total_small"
/>

<div class="text">
    <p>
		The map demonstrates that the patterns of total hourly activity are relatively constant throughout the average weekend and weekday. There are no large structural changes in the distribution of activity throughout the city. Hourly activity is concentrated around Toronto and it's surrounding large municipalities with more distant pockets having lower activity. 
	</p>
    <p>	
		Smaller patterns which can be picked up include the increase in activity at the Toronto Pearson Airport during the day and the empty space it leaves at night. The only large scale change is the general drop in activity during the night, especially seen between 3 and 5 am. The plot below shows the number of active phones in the sample during each hour throughout the week. The observed drop could be due to the nature of the mobile location data, as cell phones send out less location pings during the night. Another factor could be people commuting from outside of the GTA and leaving during the night. 
	</p>
</div>




<div class="text">
	<p>
		In the map above, the underlying population density distribution obscures the hourly changes which occur. To better visualize these changes we subtracted each cell's hourly activity by it's average hourly activity throughout the summer of 2024. This new metric measures how much more or less activity occurs in a given cell compared to it's typical activity. 
	</p>
</div>

<MapImageCycle 
	title = "Mean-subtracted hourly activity in Toronto"
	folder_weekday="exploring-daily-activity-toronto/Weekday_Difference_small"
	folder_weekend="exploring-daily-activity-toronto/Weekend_Difference_small"
/>


</main>



<style>

	main {
		background-color: #000000;
	}

    .title, .text {
        max-width: 700px;
		width: 100%;
		min-width: 350px;
        margin: 0 10px;
		color: white;
		margin: 0 auto;
    }

    .title {
		margin-top: 150px;
		margin-bottom: 25px;
	}
	
	h1 {
        margin: 0;
        padding-left: 20px;
		padding-right: 20px;
		font-family: TradeGothicBold, sans-serif;
    }

    p {
        margin: 10px 0;
        line-height: 1.5;
		padding-left: 20px;
		padding-right: 20px;
		font-family: RobotoRegular, sans-serif;
    }

</style>