<script>
    import { onMount, onDestroy, createEventDispatcher } from "svelte";
    import * as maplibregl from "maplibre-gl";
    import "maplibre-gl/dist/maplibre-gl.css";
    import * as pmtiles from "pmtiles";
    import layers from 'protomaps-themes-base';
    import metroRegionCentroids from '../data/metro_regions_centroids_no_oregon.geo.json';
    import baseMap from "../data/base_map_style.json";

    // Props
    export let handleClickOutside;
    export let metroName = "";
    export let minmax;
    export let map;
    export let selectLocation; 
    export let mapDimensionView;
    export let timePeriod = "2023-2024";
    export let changePeriodFrom = "2023-2024";
    export let changePeriodTo = "2024-2025";
    export let getZoomLevel;

    // Internal state
    let pmtilesURL = "";
    let isMapLoaded = false;
    const CHANGE_CAP = 3; // 300%
    const CHANGE_MAX_HEIGHT = 5000;

    // All periods now use merged PMTiles from one folder
    const PMTILES_FOLDER = "metro_region_geohash_stops_merged_pm";

    function getPmtilesFolder(_) {
        return PMTILES_FOLDER;
    }

    function getChangePmtilesFolder(_, __) {
        return PMTILES_FOLDER;
    }

    const dispatch = createEventDispatcher();

    // Clear metro layers and extraneous sources on the map 
    function cleanMap(map) {
        const style = map?.getStyle?.();
        if (!style || !style.layers) {
            return;
        }

        // First remove all metro layers
        style.layers.forEach((layer) => {
            // Remove metro-specific layers
            if (layer.id.endsWith('-layer') && map.getLayer(layer.id)) {
                map.removeLayer(layer.id);
            }
        });

        // Then remove corresponding sources, excluding essential ones
        Object.keys(style.sources ?? {}).forEach((sourceId) => {
            if (sourceId !== 'protomaps' && 
                sourceId !== 'centroids' && 
                sourceId !== 'metro-regions' && 
                sourceId !== 'esri-hillshade' && 
                map.getSource(sourceId)) {
                map.removeSource(sourceId);
            }
        });
    }

    // Reactive statement for map updates
	$: {
        if (map && isMapLoaded && metroName) {  // Note when metroName == '', it's boolean is false.
            const layerId = `${metroName}-layer`;

            cleanMap(map);

            const folder =
                timePeriod === 'change'
                    ? getChangePmtilesFolder(changePeriodFrom, changePeriodTo)
                    : getPmtilesFolder(timePeriod);
            const safeMetroName = encodeURI(metroName);
            pmtilesURL = `/urban-activity-atlas/${folder}/${safeMetroName}.pmtiles`;

			// Add the PMTiles source
			map.addSource(metroName, {
                type: "vector",
                url: `pmtiles://${pmtilesURL}`,
            });

            const isChangeMode = timePeriod === 'change';
            const periodMetricMap = {
                '2019-2020': 'prop_subset_stops_2019_2020',
                '2023-2024': 'prop_subset_stops_2023_2024',
                '2024-2025': 'prop_subset_stops_2024_2025',
            };

            let metricKey;
            // Change between time periods
            if (isChangeMode) {
                const fromSafe = changePeriodFrom.replace(/-/g, '_');
                const toSafe = changePeriodTo.replace(/-/g, '_');
                metricKey = `prop_subset_stops_change_${fromSafe}_to_${toSafe}`;
            } else {
                metricKey = periodMetricMap[timePeriod] ?? 'prop_subset_stops';
            }

            const metricRawExpr = ['coalesce', ['get', metricKey], 0];
            const metricExpr = isChangeMode
                ? ['max', -CHANGE_CAP, ['min', CHANGE_CAP, metricRawExpr]]
                : metricRawExpr;

            const breakpoints = [0, 0.05, 0.2, 0.35, 0.5];

            // Colours for the non-change stops
            const colors = ['#000000', '#1e3765', '#007fa3', '#6fc7ea', '#ffffff'];

            let minmax_metro = [0, 1];
            let minmax_metro_diff = 1;
            let extrusionHeightExpr = ['*', ['get', metricKey], 10000];
            let extrusionBaseExpr = 0;
            let colorExpr;

            if (!isChangeMode) {
                minmax_metro = minmax[metroName]; // Get min & max values for region
                minmax_metro_diff = minmax_metro[1] - minmax_metro[0];
                extrusionHeightExpr = ['*', ['get', metricKey], 10000 / minmax_metro[1]];
                extrusionBaseExpr = 0;
                colorExpr = [
                    'interpolate',
                    ['linear'],
                    metricExpr,
                    breakpoints[0] * minmax_metro_diff + minmax_metro[0], colors[0],
                    breakpoints[1] * minmax_metro_diff + minmax_metro[0], colors[1],
                    breakpoints[2] * minmax_metro_diff + minmax_metro[0], colors[2],
                    breakpoints[3] * minmax_metro_diff + minmax_metro[0], colors[3],
                    breakpoints[4] * minmax_metro_diff + minmax_metro[0], colors[4]
                ];
            } else {
                const changeHeightAbs = [
                    'interpolate',
                    ['linear'],
                    ['abs', metricExpr],
                    0, 0,
                    CHANGE_CAP, CHANGE_MAX_HEIGHT
                ];

                extrusionHeightExpr = changeHeightAbs;
                extrusionBaseExpr = 0;

                colorExpr = [
                    'interpolate',
                    ['linear'],
                    metricExpr,
                    -CHANGE_CAP, '#5a0000',
                    -1.5, '#a5161a',
                    -0.45, '#ff9aa0',
                    0, '#000000',
                    0.45, '#245e86',
                    CHANGE_CAP, '#002B5E'
                ];
            }

            const applyDynamicChangeScale = () => {
                if (!isChangeMode || !map.getSource(metroName) || !map.getLayer(layerId)) {
                    return;
                }

                const sourceLayer = metroName.replace(/[^\w]/g, "");
                const features = map.querySourceFeatures(metroName, { sourceLayer });
                const values = features
                    .map((feature) => Number(feature?.properties?.[metricKey]))
                    .filter((value) => Number.isFinite(value));

                if (!values.length) {
                    return;
                }

                const minValue = Math.min(...values);
                const maxValue = Math.max(...values);
                const rangeAbs = Math.max(Math.abs(minValue), Math.abs(maxValue), 1e-6);
                
                // Colour range for the relative change in stops
                const dynamicColorExpr = [
                    'interpolate',
                    ['linear'],
                    metricRawExpr,
                    -rangeAbs, '#ff9aa0',
                    -rangeAbs * 0.15, '#8f232c',
                    0, '#000000',
                    rangeAbs * 0.15, '#245e86',
                    rangeAbs, '#6fc7ea'
                ];

                const colorPaintProperty = mapDimensionView === "3D"
                    ? 'fill-extrusion-color'
                    : 'fill-color';
                map.setPaintProperty(layerId, colorPaintProperty, dynamicColorExpr);

                if (mapDimensionView === "3D") {
                    const heightScale = CHANGE_MAX_HEIGHT / rangeAbs;
                    const dynamicHeightAbsExpr = ['*', ['abs', metricRawExpr], heightScale];

                    map.setPaintProperty(layerId, 'fill-extrusion-height', dynamicHeightAbsExpr);
                    map.setPaintProperty(layerId, 'fill-extrusion-base', 0);
                }
            };

            // toggle layer style depending if 2D or 3D view
            if (mapDimensionView === "3D") {

                map.addLayer({
                    "id": layerId,
                    "type": "fill-extrusion",
                    "source": metroName,
                    "source-layer": metroName.replace(/[^\w]/g, ""),
                    'paint': {
                        'fill-extrusion-color': colorExpr,
                        'fill-extrusion-height': extrusionHeightExpr,
                        'fill-extrusion-base': extrusionBaseExpr,
                        // 'fill-extrusion-height': 10000,
                        'fill-extrusion-opacity': 1 // Adjust opacity as needed
                    },
                    "minzoom": 5  // Add this line to match metro-areas visibility
                }, "water_outline");
            

            } else {
                map.addLayer({
                    "id": layerId,
                    "type": "fill",
                    "source": metroName,
                    "source-layer": metroName.replace(/[^\w]/g, ""),
                    'paint': {
                        'fill-color': colorExpr,
                        'fill-opacity': 1 // Adjust opacity as needed
                    },
                    "minzoom": 5  // Add this line to match metro-areas visibility
                }, "water_outline");
            }            

            if (isChangeMode) {
                if (map.isSourceLoaded(metroName)) {
                    applyDynamicChangeScale();
                } else {
                    map.once('idle', applyDynamicChangeScale);
                }
            }
            
            // Update the filters to show/hide appropriate regions
            map.setFilter('metro-areas', ['!=', ['get', 'name'], metroName]);  // Show all except selected
            map.setFilter('selected-metro-outline', ['==', ['get', 'name'], metroName]);  // Show only selected outline
        } else if (map && isMapLoaded) {
            cleanMap(map);

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
                glyphs: "https://schoolofcities.github.io/fonts/fonts/{fontstack}/{range}.pbf",
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
            center: [-93, 41],
            zoom: getZoomLevel().initZoom,
            maxZoom: 13,
            minZoom: getZoomLevel().minZoom,
            bearing: 0,
            pitch: 0,
            attributionControl: false
        });

        // console.log(layers("protomaps", "dark"));

        map.addControl(new maplibregl.NavigationControl(), "top-right");
        map.addControl(new maplibregl.ScaleControl(), "bottom-right");

        map.on('style.load', () => {
            map.setProjection({
                type: (map.getZoom() < 5) ? 'globe' : 'mercator'
            });
            map.on('zoom', () => {
                const zoom = map.getZoom();
                map.setProjection({
                    type: (zoom < 5) ? 'globe' : 'mercator'
                });
            });
        });

        map.on('load', () => {
            isMapLoaded = true;

            // map.addSource('esri-hillshade', {
            //     'type': 'raster',
            //     'tiles': [
            //         'https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}'
            //     ],
            //     'tileSize': 256
            // });
            // map.addLayer({
            //     'id': 'esri-hillshade',
            //     'type': 'raster',
            //     'source': 'esri-hillshade',
            //     'paint': {
            //         'raster-opacity': 0.08
            //     }
            // });

            // Add centroids source
            map.addSource('centroids', {
                type: 'geojson',
                data: metroRegionCentroids
            });

            // Add PMTiles source for metro regions boundaries
            map.addSource('metro-regions', {
                type: 'vector',
                url: 'pmtiles://metro_regions_full_no_oregon.pmtiles'
            });

            // Add secret hidden centroids layer for clicking with wide radius
            map.addLayer({
                id: 'metro-points-click-target', 
                type: 'circle',
                source: 'centroids',
                paint: {
                    'circle-radius': 20,  // Larger radius for easier clicking
                    'circle-color': '#000000',
                    'circle-opacity': 0,  // Make it invisible
                },
                maxzoom: 5
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
                'source-layer': 'metro_region_full',  // Updated layer name
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
                'source-layer': 'metro_region_full',  // Updated layer name
                paint: {
                    'line-color': '#6FC7EA',//'#fff',
                    'line-opacity': 0.6,
                    'line-width': 2,
                    // 'line-dasharray': [4, 2] 
                },
                filter: ['has', 'name'],  // Show all by default
                minzoom: 5
            });

            // Add a new layer for the selected region's outline
            map.addLayer({
                id: 'selected-metro-outline',
                type: 'line',
                source: 'metro-regions',
                'source-layer': 'metro_region_full',  // Updated layer name
                paint: {
                    'line-color': '#6FC7EA',//'#94928a',
                    'line-opacity': 0.9,
                    'line-width': 4,
                    // 'line-dasharray': [6, 3, 3, 3] 
                },
                filter: ['==', ['get', 'name'], ''],  // Start with empty filter
                minzoom: 5,
                maxzoom: 11
            });

            // Update metro region across the whole application using selectLocation
            map.on('click', 'metro-points-click-target', (e) => { 
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
            ['metro-points-click-target', 'metro-areas'].forEach(layer => {  
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
        isMapLoaded = false;
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