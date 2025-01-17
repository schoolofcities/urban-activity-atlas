<script>
    import { onMount, onDestroy, createEventDispatcher } from "svelte";
    import * as maplibregl from "maplibre-gl";
    import "maplibre-gl/dist/maplibre-gl.css";
    import * as pmtiles from "pmtiles";
    import layers from 'protomaps-themes-base';
    import metroRegionCentroids from '../data/metro_regions_centroids.geo.json';
    import metroRegionsSimple from '../data/metro_regions_simple.geo.json';
    import baseMap from "../data/base_map_style.json";

    // Props
    export let handleClickOutside;
    export let metroName = "";
    export let minmax;
    export let map;
    export let selectLocation; 

    // Internal state
    let pmtilesURL = "";

    const dispatch = createEventDispatcher();

    // Reactive statement for map updates
	$: {
        if (map && metroName) {



            const layerId = `${metroName}-layer`;

			// Remove all metro layers
			map.getStyle().layers.forEach((layer) => {
				if (layer.id.endsWith('-layer') && map.getLayer(layer.id)) {
					// console.log(`Removing metro layer: ${layer.id}`);
					map.removeLayer(layer.id);
				}
			});

			// Remove all metro sources
			Object.keys(map.style.sourceCaches).forEach((sourceId) => {
				if (sourceId !== 'protomaps' && map.getSource(sourceId)) {
					// console.log(`Removing metro source: ${sourceId}`);
					map.removeSource(sourceId);
				}
			});

            pmtilesURL = `http://localhost:5173/metro_region_geohash_stops_pm/${metroName.replace(/ /g, '%20')}.pmtiles`;

			console.log('pmtilesURL: ', pmtilesURL);

			// Add the PMTiles source
			map.addSource(metroName, {
                type: "vector",
                url: `pmtiles://${pmtilesURL}`,
            });

            const minmax_metro = minmax[metroName]; // Get min & max values for region
            console.log('minmax_metro:', minmax_metro);
            const minmax_metro_diff = minmax_metro[1] - minmax_metro[0]

            const breakpoints = [0, 0.05, 0.2, 0.35, 0.5];
            const colors = ['#000000', '#1e3765', '#007fa3', '#6fc7ea', '#c1edff'];

            map.addLayer({
                    "id": layerId,
                    "type": "fill",
                    "source": metroName,
                    "source-layer": metroName.replace(/[^\w]/g, ""),
                    // paint: {
                    //     "fill-opacity": 0.65,
                    //     "fill-color": [
                    //         "interpolate", 
                    //         ["cubic-bezier", 0.1, 0.01, 1.0, 1.0], // ["exponential", 2], // https://maplibre.org/maplibre-style-spec/expressions/#interpolate - NEED TO FIX THIS
                    //         ["get", "prop_subset_stops"],
                    //         minmax_metro[0], "#0b513f",    // Lower value - green
                    //         minmax_metro[1], "#fffb85"     // Higher value - yellow
                    //     ],
                    //     "fill-outline-color": "rgba(0, 0, 0, 0)",
                    // },
                    'paint': {
                        'fill-color': [
                            'interpolate',
                            ['linear'], // Use linear interpolation
                            ['get', 'prop_subset_stops'], // Replace with your numeric property
                            breakpoints[0] * minmax_metro_diff + minmax_metro[0], colors[0],
                            breakpoints[1] * minmax_metro_diff + minmax_metro[0], colors[1],
                            breakpoints[2] * minmax_metro_diff + minmax_metro[0], colors[2],
                            breakpoints[3] * minmax_metro_diff + minmax_metro[0], colors[3],
                            breakpoints[4] * minmax_metro_diff + minmax_metro[0], colors[4]
                        ],
                        'fill-opacity': 1 // Adjust opacity as needed
                    },
                    "minzoom": 5  // Add this line to match metro-areas visibility
                }, "water_outline");
            
            // Update the filters to show/hide appropriate regions
            map.setFilter('metro-areas', ['!=', ['get', 'name'], metroName]);  // Show all except selected
            map.setFilter('selected-metro-outline', ['==', ['get', 'name'], metroName]);  // Show only selected outline
		} else if (map) {
            // When no region selected, show all regions and no outline
            map.setFilter('metro-areas', ['has', 'name']);  // Show all regions
            map.setFilter('selected-metro-outline', ['==', ['get', 'name'], '']);  // Hide outline
        }
    }

    onMount(() => {
        let protocol = new pmtiles.Protocol();
        maplibregl.addProtocol("pmtiles", protocol.tile);

        document.addEventListener('click', handleClickOutside);

        map = new maplibregl.Map({
            container: "map", 
            style: {
                version: 8,
                glyphs: 'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
                sprite: "https://protomaps.github.io/basemaps-assets/sprites/v4/dark",
                sources: {
                    'protomaps': {
                        type: 'vector',
                        url: 'https://api.protomaps.com/tiles/v4.json?key=f1d93c3bd5c79742',
                        attribution: '<a href="https://protomaps.com">Protomaps</a> © <a href="https://openstreetmap.org">OpenStreetMap</a>'
                    }
                },
                layers: baseMap
            },
            center: [-104.048, 44.511],
            zoom: 3.5,
            maxZoom: 13,
            minZoom: 3,
            attributionControl: true
        });

        console.log(layers("protomaps", "dark"));

        map.addControl(new maplibregl.NavigationControl(), "top-right");
        map.addControl(new maplibregl.ScaleControl(), "bottom-right");

        map.on('load', () => {

            map.addSource('esri-hillshade', {
                'type': 'raster',
                'tiles': [
                    'https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}'
                ],
                'tileSize': 256
            });
            map.addLayer({
                'id': 'esri-hillshade',
                'type': 'raster',
                'source': 'esri-hillshade',
                'paint': {
                    'raster-opacity': 0.08
                }
            });

            // Add centroids source
            map.addSource('centroids', {
                type: 'geojson',
                data: metroRegionCentroids
            });

            // Add metro regions source
            map.addSource('metro-regions', {
                type: 'geojson',
                data: metroRegionsSimple
            });

            // Add centroids layer (visible at low zoom)
            map.addLayer({
                id: 'metro-points',
                type: 'circle',
                source: 'centroids',
                paint: {
                    'circle-radius': 6,
                    'circle-color': '#6FC7EA',
                    'circle-stroke-width': 1,
                    'circle-stroke-color': '#1E3765'
                },
                maxzoom: 5 // Only show points when zoomed out
            });

            // Regular metro areas layer (for non-selected regions)
            map.addLayer({
                id: 'metro-areas',
                type: 'fill',
                source: 'metro-regions',
                paint: {
                    'fill-color': '#000000',
                    'fill-opacity': 0.9
                },
                filter: ['has', 'name'],  // Show all by default
                minzoom: 5
            }, "water_outline");
            map.addLayer({
                id: 'metro-area-outlines',
                type: 'line',
                source: 'metro-regions',
                paint: {
                    'line-color': '#fff',
                    'line-opacity': 0.4,
                    'line-width': 1,
                    'line-dasharray': [4, 2] 
                },
                filter: ['has', 'name'],  // Show all by default
                minzoom: 5
            });

            // Add a new layer for the selected region's outline
            map.addLayer({
                id: 'selected-metro-outline',
                type: 'line',
                source: 'metro-regions',
                paint: {
                    'line-color': '#94928a',
                    'line-width': 2,
                    'line-dasharray': [6, 3, 3, 3] 
                },
                filter: ['==', ['get', 'name'], ''],  // Start with empty filter
                minzoom: 5,
                maxzoom: 11
            });

            // Update metro region across the whole application using selectLocation
            map.on('click', 'metro-points', (e) => {
                if (e.features.length > 0) {
                    selectLocation(e.features[0].properties.name);
                }
            });

            map.on('click', 'metro-areas', (e) => {
                if (e.features.length > 0) {
                    selectLocation(e.features[0].properties.name);
                }
            });

            // Add hover effects
            ['metro-points', 'metro-areas'].forEach(layer => {
                map.on('mouseenter', layer, () => {
                    map.getCanvas().style.cursor = 'pointer';
                });
                map.on('mouseleave', layer, () => {
                    map.getCanvas().style.cursor = '';
                });
            });

            // Dispatch event when map and layers are fully loaded
            dispatch('mapInit');
        });
    });

    onDestroy(() => {
        if (map) {
            map.remove();
        }
    });
</script>

<div id="map"></div>

<style>
    #map {
        background-color: black;
        height: 100%;
        width: 100%;
    }
</style>