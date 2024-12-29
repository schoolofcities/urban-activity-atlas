<script>
	import "../assets/global-styles.css";
	
	import { onMount } from "svelte";
	
	import * as maplibregl from "maplibre-gl"; 
	import "maplibre-gl/dist/maplibre-gl.css";
	import * as pmtiles from "pmtiles";
	import layers from 'protomaps-themes-base'; // eventually switch this out for our own theme

	// Enter URL below into PMTiles Viewer (https://pmtiles.io) to see map, and layer & property names
	let pmtilesURL = "http://localhost:5173/metro_region_geohash_stops_pm/Abilene,%20TX.pmtiles"; // (local) development only

	let map = null;

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
			center: [-99.709, 32.526],
			zoom: 9,
			maxZoom:16,
			minZoom: 2,
			// @ts-ignore
			attributionControl: true
		});

		map.addControl(new maplibregl.NavigationControl(), "top-right");
		map.addControl(new maplibregl.ScaleControl(), "bottom-right");

		map.on('load', () => {

			map.addSource('abilene-tx', {
				type: 'vector',
				url: "pmtiles://" + pmtilesURL,
			});

			map.addLayer({
				'id': 'abilene-tx-layer',
				'type': 'fill',
				'source': 'abilene-tx',
				'source-layer': 'AbileneTX',
				'paint': {
					'fill-opacity': .8,
					'fill-color': [
						'step',
						['get', 'prop_subset_stops'],
						'#0b513f',
						0.00000064, '#397c53', // when I add other metros - use quintiles instead of specific cutoffs
						0.00000141, '#70a863',
						0.00000219, '#b2d372',
						0.00000296, '#fffb85'
					],
					'fill-outline-color': 'rgba(0, 0, 0, 0)' // get rid of the outline
				},
			});
		});
	});

</script>

<div class="container">
	<div class="panel">
		<ul class="legend">
			<li><span style="background-color: #0b513f;"></span>Low</li> <!-- &lt; 0.00000064 -->
			<li><span style="background-color: #397c53;"></span></li> <!-- ≥ 0.00000064 -->
			<li><span style="background-color: #70a863;"></span></li> <!-- ≥ 0.00000141 -->
			<li><span style="background-color: #b2d372;"></span></li> <!-- ≥ 0.00000219 -->
			<li><span style="background-color: #fffb85;"></span>High</li> <!-- ≥ 0.00000296 -->
		</ul>
	</div>

	<div id="map">
	</div>
</div>


<style>

	.legend {
		list-style: none;
		padding: 0;
		margin: 30px;		
	}

	.legend li {
		display: flex;
		align-items: center;
		margin: 8px;
	}
	
	.legend span {
		display: inline-block;
		width: 20px; /* Width of color box */
		height: 20px; /* Height of color box */
		margin-right: 10px; /* Spacing between box and text */
		/* border: 1px solid #000; Optional: Add a border for better visibility */
	}

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
		/* border-right: solid 2px var(--brandRed); */
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