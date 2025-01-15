<script>
    import { onMount, onDestroy } from "svelte";
    import * as maplibregl from "maplibre-gl";
    import "maplibre-gl/dist/maplibre-gl.css";
    import * as pmtiles from "pmtiles";
    import layers from 'protomaps-themes-base';
    import metroRegionCentroids from '../data/metro_regions_centroids.geo.json';
    import metroRegionsSimple from '../data/metro_regions_simple.geo.json';

    // Props
    export let handleClickOutside;
    export let metroName = "";
    export let minmax;
    export let map;
    export let selectLocation; // Add this prop

    // Internal state
    let pmtilesURL = "";

    // Reactive statement for map updates
	$: {
        if (map && metroName) {
            // console.log('Adding source and layer for', metroName);
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

            map.addLayer({
                    id: layerId,
                    type: "fill",
                    source: metroName,
                    "source-layer": metroName.replace(/[^\w]/g, ""),
                    paint: {
                        "fill-opacity": 0.65,
                        "fill-color": [
                            "interpolate", 
                            ["cubic-bezier", 0.1, 0.01, 1.0, 1.0], // ["exponential", 2], // https://maplibre.org/maplibre-style-spec/expressions/#interpolate - NEED TO FIX THIS
                            ["get", "prop_subset_stops"],
                            minmax_metro[0], "#0b513f",    // Lower value - green
                            minmax_metro[1], "#fffb85"     // Higher value - yellow
                        ],
                        "fill-outline-color": "rgba(0, 0, 0, 0)",
                    },
                });
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
                layers: layers("protomaps", "dark") 
            },
            center: [-104.048, 44.511],
            zoom: 3.5,
            maxZoom: 16,
            minZoom: 3,
            attributionControl: true
        });

        map.addControl(new maplibregl.NavigationControl(), "top-right");
        map.addControl(new maplibregl.ScaleControl(), "bottom-right");

        map.on('load', () => {
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
                    'circle-color': '#70a863',
                    'circle-stroke-width': 1,
                    'circle-stroke-color': '#fff'
                },
                maxzoom: 5 // Only show points when zoomed out
            });

            // Add metro regions layer (visible at high zoom)
            map.addLayer({
                id: 'metro-areas',
                type: 'fill',
                source: 'metro-regions',
                paint: {
                    'fill-color': '#70a863',
                    'fill-opacity': 0.3,
                    'fill-outline-color': '#fff'
                },
                minzoom: 5 // Only show regions when zoomed in
            });

            // Update click handlers to use selectLocation
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
        height: 100%;
        width: 100%;
    }
</style>