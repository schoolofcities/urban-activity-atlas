<script>
	import "../assets/global-styles.css";
	
	import { onMount } from "svelte";
	
	import * as maplibregl from "maplibre-gl"; 
	import "maplibre-gl/dist/maplibre-gl.css";
	import * as pmtiles from "pmtiles";
	import layers from 'protomaps-themes-base'; // eventually switch this out for our own theme

	let map;

	onMount(() => {
		let protocol = new pmtiles.Protocol();
		maplibregl.addProtocol("pmtiles", protocol.tile);

		map = new maplibregl.Map({
			container: "map", 
			style: {
				version: 8,
				// "glyphs": "https://schoolofcities.github.io/fonts/fonts/{fontstack}/{range}.pbf",
				glyphs:'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
    			sprite: "https://protomaps.github.io/basemaps-assets/sprites/v4/dark",
				sources: {
					'protomaps': {
						type: 'vector',
						url: 'https://api.protomaps.com/tiles/v4.json?key=f1d93c3bd5c79742',
						attribution: '<a href="https://protomaps.com">Protomaps</a> © <a href="https://openstreetmap.org">OpenStreetMap</a>'
					}
				},
				// @ts-ignore
				layers: layers("protomaps","dark") // sub out for our own layer styles eventually
			},
			center: [-84, 42.],
			zoom: 6,
			maxZoom:16,
			minZoom: 2,
			// @ts-ignore
			attributionControl: true
		});

		map.addControl(new maplibregl.NavigationControl(), "top-right");
	});

</script>

<div class="container">
	<div class="panel">
		hello
	</div>

	<div id="map">
	</div>
</div>


<style>
	.container {
		display: flex;
	}

	.panel {
		width: 420px;
		min-width: 420px;
		height: 420px;
		height: 100vh;
		overflow: auto;
		overflow-x: hidden;
		background-color: var(--brandWhite); 
		border-right: solid 2px var(--brandRed);
	}

	#map {
		height: 100vh;
		width: calc(100vw - 420px);
		min-width: 420px;
		background-color: var(--brandLightBlue); 
	}

	@media screen and (max-width: 820px) {
		.container {
			flex-direction: column-reverse;
		}

		#map {
			height: 50vh;
			width: 100vw;
		}

		.panel {
			height: calc(50vh - 1px);
			width: 100vw;
			border-top: solid 1px var(--brandGray);
			border-right: none;
		}
	}
</style>