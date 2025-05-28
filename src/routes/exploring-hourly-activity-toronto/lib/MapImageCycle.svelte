<script>
	import { onMount, onDestroy } from 'svelte';

	export let title = '';
	export let folder_weekday = '';
	export let folder_weekend = '';
	export let legendColors = [];
	export let legendLabels = [];

	let folder;
	let currentHour = 0;
	let interval = null;
	let isPlaying = false;
	let imagesLoaded = false;
	let decodedImages = [];

	$: imagePaths = Array.from({ length: 24 }, (_, i) => `/urban-activity-atlas/${folder}/Hour_${i}.png`);
	$: ticks = Array.from({ length: 24 }, (_, i) => i);

	let selectedMode = 'weekday';

	function switchMode(mode) {
		if (mode === 'weekday') {
			folder = folder_weekday;
		} else {
			folder = folder_weekend;
		}
		selectedMode = mode;
		loadImages();
	}

	async function loadImages() {
  imagesLoaded = false;
  decodedImages = [];

  // PHASE 1: Critical first frame (0ms delay)
  await loadSingleImage(imagePaths[0]); 
  
  // PHASE 2: Next 3 visible hours (50ms delay to avoid blocking)
  setTimeout(async () => {
    await Promise.all([
      loadSingleImage(imagePaths[1]),
      loadSingleImage(imagePaths[2]),
      loadSingleImage(imagePaths[3])
    ]);
  }, 50);

  // PHASE 3: Remaining images during idle time
  imagePaths.slice(4).forEach(img => {
    requestIdleCallback(() => loadSingleImage(img), { timeout: 2000 });
  });

  imagesLoaded = true; 
}

async function loadSingleImage(src) {
	const img = new Image();
	img.src = src;
	img.decoding = "async"; 
	await img.decode().catch(() => {});
	decodedImages.push(src);
}


	onMount(() => {
		switchMode('weekday');
	});

	onDestroy(() => {
		clearInterval(interval);
	});

	function play() {
		if (!isPlaying && imagesLoaded) {
			isPlaying = true;
			interval = setInterval(() => {
				currentHour = (currentHour + 1) % 24;
			}, 250);
		}
	}

	function stop() {
		isPlaying = false;
		clearInterval(interval);
	}



</script>


<div class="container">

	<h3>{title}</h3>

	<div class="legend-container">
		<div class="gradient-legend" 
			 style="background: linear-gradient(to right, {legendColors.join(',')})">
		</div>
		<div class="legend-labels">
			{#each legendLabels as label, i}
				<span class="label-{i}">{label}</span>
			{/each}
		</div>
	  </div>

	<div class="controls">
		<div class="range-play-wrapper">
			{#if !isPlaying}
				<button on:click={play} aria-label="Play"  disabled={!imagesLoaded}>
					<svg width="12" height="12" viewBox="0 0 12 12" fill="white" xmlns="http://www.w3.org/2000/svg">
						<polygon points="2,1 10,6 2,11" />
					</svg>
				</button>
			{:else}
				<button aria-label="Stop" on:click={stop}>
					<svg width="12" height="12" viewBox="0 0 12 12" fill="white" xmlns="http://www.w3.org/2000/svg">
						<rect x="2" y="2" width="8" height="8" />
					</svg>
				</button>
			{/if}

			<div class="slider-wrapper">
				<input
					type="range"
					min="0"
					max="23"
					bind:value={currentHour}
					step="1"
					disabled={!imagesLoaded}
					class="custom-slider"
				/>
				<div class="ticks">
					{#each ticks as t}
						<span>{t}</span>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<div class="mode-toggle">
		<button
			class:selected={selectedMode === 'weekday'}
			on:click={() => switchMode('weekday')}
		>
			Weekday
		</button>
		<button
			class:selected={selectedMode === 'weekend'}
			on:click={() => switchMode('weekend')}
		>
			Weekend
		</button>
	</div>
	
	<img
		loading="lazy"
  		decoding="async"
		src={imagesLoaded ? imagePaths[currentHour] : './urban-activity-atlas/exploring-daily-activity-toronto/blank-image.png'}
		alt={`Hour ${currentHour}`}
		class:loading={!imagesLoaded}
	/>
</div>


<style>
	.container {
		width: 100%;
		max-width: 540px;
		margin: 0 auto;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.legend-container {
		width: 100%;
		max-width: 470px;
		margin: 0 auto;
		margin-top: 10px;
		margin-bottom: 0px;
	}
	
	.gradient-legend {
		height: 8px;
		width: 100%;
		border-radius: 0px;
		margin-bottom: 5px;
	}

	.legend-labels {
		display: flex;
		justify-content: space-between;
		width: 100%;
		position: relative;
	}
	
	.legend-labels span {
		font-size: 10px;
		color: white;
		padding-left: 3px;
		padding-right: 3px;
	}
	
	/* 2-label version */
	.legend-labels span:first-child:nth-last-child(2),
	.legend-labels span:last-child:nth-first-child(2) {
		flex: 1;
	}
	
	/* 3-label version */
	.legend-labels span:first-child:nth-last-child(3),
	.legend-labels span:last-child:nth-first-child(3) {
		flex: 1;
	}
	
	.legend-labels span:first-child {
		text-align: left;
	}
	
	.legend-labels span:last-child {
		text-align: right;
	}
	
	/* Only applies when there's 3 labels */
	.legend-labels span:nth-child(2) {
		text-align: center;
	}

	img {
		width: 100%;
		height: auto;
		display: block;
	}

	.controls {
		width: calc(100% - 60px);
		box-sizing: border-box;
		margin-top: 1rem;
		text-align: center;
		padding-inline: 1rem;
		color: white;
	}

	.range-play-wrapper {
		display: flex;
		align-items: center;
		gap: 1rem;
		width: 100%;
	}

	button {
		padding: 0px;
		padding-left: 5px;
		padding-right: 5px;
		width: 24px;
		height: 24px;
		background-color: black;
		color: white;
		border: 1px solid var(--brandGray70);
		border-radius: 0;
		cursor: pointer;
		font-size: 16px;
		opacity: 1;
		transition: opacity 0.2s ease;
		white-space: nowrap;
	}

	button:hover {
		opacity: 0.8;
	}

	.slider-wrapper {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: stretch;
	}

	input[type="range"].custom-slider {
		width: 100%;
		appearance: none;
		height: 2px;
		background: var(--brandGray);
		border-radius: 1px;
		cursor: pointer;
	}

	input[type="range"].custom-slider::-webkit-slider-thumb {
		appearance: none;
		width: 10px;
		height: 10px;
		background: white;
		border: 1px solid white;
		border-radius: 50%;
		cursor: pointer;
	}

	input[type="range"].custom-slider::-moz-range-thumb {
		width: 10px;
		height: 10px;
		background: white;
		border: 1px solid white;
		border-radius: 50%;
		cursor: pointer;
	}

	input[type="range"].custom-slider::-ms-thumb {
		width: 10px;
		height: 10px;
		background: white;
		border: 1px solid white;
		border-radius: 50%;
		cursor: pointer;
	}

	.ticks {
		display: grid;
		grid-template-columns: repeat(24, 1fr);
		font-size: 10px;
		font-family: RobotoRegular;
		font-weight: normal;
		margin-top: 5px;
		margin-left: -3px;
		margin-right: -6px;
		color: white;
	}

	.ticks span {
		text-align: center;
	}

	@media (max-width: 450px) {
		.ticks {
			font-size: 8px;
		}
	}

	h3 {
		font-family: TradeGothicBold;
		font-weight: normal;
		font-size: 23px;
		max-width: 530px;
		color: white;
		margin-bottom: 0px;
		padding-left: 15px;
		padding-right: 15px;
	}

	.mode-toggle {
		margin-top: 1rem;
		display: flex;
		gap: 1rem;
		justify-content: center;
	}

	.mode-toggle button {
		background: black;
		width: 100px;
		color: white;
		border: 1px solid var(--brandGray);
		font-family: RobotoRegular;
		font-weight: normal;
		padding: 2px;
		cursor: pointer;
		font-size: 12px;
		transition: background 0.2s ease, opacity 0.2s ease;
		opacity: 0.5;
	}

	.mode-toggle button.selected {
		opacity: 1
	}
</style>
