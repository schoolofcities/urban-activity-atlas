<script>

	import TopSofC from '$lib/TopSofC.svelte';
    import '../../assets/global-styles.css';
</script>


<TopSofC/>

<div class="title">
    <h1>Exploring daily activity in Toronto</h1>
</div>

<div class="text">
    <p>
		Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.
	</p>
    <p>
		Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
	</p>
	<p>
		Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
	</p>
</div>


<style>

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