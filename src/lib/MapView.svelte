<script>
    import { onMount, onDestroy, createEventDispatcher } from "svelte";
    import { base } from '$app/paths';
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
    export let timePeriod = "2025-2026";
    export let changePeriodFrom = "2024-2025";
    export let changePeriodTo = "2025-2026";
    export let getZoomLevel;
    export let showTransitOverlay = true;
    // export let transitDataMode = "protomaps";
    export let transitMinZoom = 7;

    // Transit layer colors from global brand palette
    const TRANSIT_COLORS = {
        subway: '#DC4633',       // --brandRed
        lightRail: '#8DBF2E',    // --brandLightGreen
        tram: '#F1C500'          // --brandYellow
    };

    // Internal state
    let isMapLoaded = false;
    let isTransitReady = false;
    let transitFetchController;
    let transitRequestId = 0;
    const dispatch = createEventDispatcher();

const TRANSIT_SOURCE_ID = "transit-geojson";
const TRANSIT_LAYER_IDS = ["transit-fill", "transit-points", "transit-subway", "transit-light-rail", "transit-tram"];
const CHANGE_CAP = 3;
const CHANGE_MAX_HEIGHT = 5000;

// All periods currently use merged PMTiles from one folder.
const PMTILES_FOLDER = "metro_region_geohash_stops_merged_pm_v9_2";

function getPmtilesFolder(_) {
    return PMTILES_FOLDER;
}

function getChangePmtilesFolder(_, __) {
    return PMTILES_FOLDER;
}

function cleanMap(map) {
    const style = map?.getStyle?.();
    if (!style) {
        return;
    }

    const reservedSources = new Set(['protomaps', 'centroids', 'metro-regions', TRANSIT_SOURCE_ID]);

    for (const layer of style.layers ?? []) {
        if (layer.id.endsWith('-layer') && map.getLayer(layer.id)) {
            map.removeLayer(layer.id);
        }
    }

    for (const sourceId of Object.keys(style.sources ?? {})) {
        if (!reservedSources.has(sourceId) && map.getSource(sourceId)) {
            map.removeSource(sourceId);
        }
    }
}

function removeTransitLayers(map) {
    TRANSIT_LAYER_IDS.forEach((layerId) => {
        if (map.getLayer(layerId)) map.removeLayer(layerId);
    });
    if (map.getSource(TRANSIT_SOURCE_ID)) map.removeSource(TRANSIT_SOURCE_ID);
}

function ensureTransitLayers(map) {
    if (!map.getSource(TRANSIT_SOURCE_ID)) {
        map.addSource(TRANSIT_SOURCE_ID, {
            type: "geojson",
            data: `${base}/export.geojson`
        });
    }

    if (!map.getLayer('transit-fill')) {
        map.addLayer({
            id: 'transit-fill',
            type: 'fill',
            source: TRANSIT_SOURCE_ID,
            filter: [
                'any',
                ['==', ['geometry-type'], 'Polygon'],
                ['==', ['geometry-type'], 'MultiPolygon']
            ],
            paint: {
                'fill-color': '#65c9d7',
                'fill-opacity': 0.18
            }
        }, 'selected-metro-outline');
    }

    if (!map.getLayer('transit-points')) {
        map.addLayer({
            id: 'transit-points',
            type: 'circle',
            source: TRANSIT_SOURCE_ID,
            filter: ['==', ['geometry-type'], 'Point'],
            paint: {
                'circle-radius': 5,
                'circle-color': '#65c9d7',
                'circle-stroke-color': '#ffffff',
                'circle-stroke-width': 1,
                'circle-opacity': 0.9
            }
        }, 'selected-metro-outline');
    }

    const layerConfigs = [
        {
            id: "transit-subway",
            filter: ["==", ["get", "railway"], "subway"],
            lineColor: TRANSIT_COLORS.subway,
            minZoom: transitMinZoom,
            width: [1.8, 2.6, 3.4],
            opacity: [0.6, 0.72, 0.8]
        },
        {
            id: "transit-light-rail",
            filter: ["in", ["get", "railway"], ["literal", ["light_rail", "monorail", "funicular"]]],
            lineColor: TRANSIT_COLORS.lightRail,
            minZoom: Math.max(transitMinZoom, 7),
            width: [1.6, 2.4, 3.2],
            opacity: [0.4, 0.5, 0.62]
        },
        {
            id: "transit-tram",
            filter: ["==", ["get", "railway"], "tram"],
            lineColor: TRANSIT_COLORS.tram,
            minZoom: Math.max(transitMinZoom, 8),
            width: [1.0, 1.5, 2.1],
            opacity: [0.36, 0.48, 0.6]
        }
    ];

    layerConfigs.forEach(({ id, filter, lineColor, minZoom, width, opacity }) => {
        if (map.getLayer(id)) return;

        map.addLayer({
            id,
            type: "line",
            source: TRANSIT_SOURCE_ID,
            filter,
            paint: {
                "line-color": lineColor,
                "line-opacity": [
                    "interpolate", ["linear"], ["zoom"],
                    minZoom, opacity[0],
                    minZoom + 3, opacity[1],
                    minZoom + 6, opacity[2]
                ],
                "line-width": [
                    "interpolate", ["linear"], ["zoom"],
                    minZoom, width[0],
                    minZoom + 3, width[1],
                    minZoom + 6, width[2]
                ]
            },
            minzoom: minZoom
        }, "selected-metro-outline");
    });
}

function syncTransitOverlay(map) {
    if (!isMapLoaded) return;

    ensureTransitLayers(map);

    const showTransit = showTransitOverlay;
    TRANSIT_LAYER_IDS.forEach((layerId) => {
        if (map.getLayer(layerId)) {
            map.setLayoutProperty(layerId, "visibility", showTransit ? "visible" : "none");
        }
    });
}

    // Adjust camera view when dimension view changes
    $: {
        if (map && isMapLoaded) {
            if (mapDimensionView === "3D") {
                map.easeTo({ pitch: 65, bearing: 45, duration: 1000 }); // Pitch up and point slightly left
            } else {
                map.easeTo({ pitch: 0, bearing: 0, duration: 1000 }); // Reset strictly to top-down north-up
            }
        }
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

			// Add the PMTiles source
			map.addSource(metroName, {
                type: "vector",
                url: `pmtiles://${base ? `${base}/` : ''}${folder}/${safeMetroName}.pmtiles`,
            });

            const isChangeMode = timePeriod === 'change';
            const periodMetricMap = {
                '2019-2020': 'prop_subset_stops_2019_2020',
                '2024-2025': 'prop_subset_stops_2024_2025',
                '2025-2026': 'prop_subset_stops_2025_2026',
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
                    return false;
                }

                const sourceLayer = metroName.replace(/[^\w]/g, "");
                const features = map.querySourceFeatures(metroName, { sourceLayer });
                const values = features
                    .map((feature) => Number(feature?.properties?.[metricKey]))
                    .filter((value) => Number.isFinite(value));

                if (!values.length) {
                    return false;
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
                
                return true;
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
                }, "water");
            

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
                }, "water");
            }            

            if (isChangeMode) {
                const tryApplyScale = (e) => {
                    if (e && e.sourceId && e.sourceId !== metroName) return;
                    if (map.isSourceLoaded(metroName)) {
                        const success = applyDynamicChangeScale();
                        if (success) {
                            map.off('sourcedata', tryApplyScale);
                        }
                    }
                };

                if (map.isSourceLoaded(metroName)) {
                    const success = applyDynamicChangeScale();
                    if (!success) {
                        map.on('sourcedata', tryApplyScale);
                    }
                } else {
                    map.on('sourcedata', tryApplyScale);
                }
            }
            
            // Update the filters to show/hide appropriate regions
            map.setFilter('metro-areas', ['!=', ['get', 'name'], metroName]);  // Show all except selected
            map.setFilter('selected-metro-outline', ['==', ['get', 'name'], metroName]);  // Show only selected outline

            syncTransitOverlay(map);
        } else if (map && isMapLoaded) {
            cleanMap(map);

            syncTransitOverlay(map);

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
                    'fill-opacity': 0.97
                },
                filter: ['has', 'name'],  // Show all by default
                minzoom: 5
            }, "water");
            map.addLayer({
                id: 'metro-area-outlines',
                type: 'line',
                source: 'metro-regions',
                'source-layer': 'metro_region_full',  // Updated layer name
                paint: {
                    'line-color': '#fff',//'#fff',
                    'line-opacity': 0.6,
                    'line-width': 1,
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
                    'line-color': '#fff',//'#94928a',
                    'line-opacity': 0.79,
                    'line-width': 2,
                    'line-dasharray': [1,1,2,1] 
                },
                filter: ['==', ['get', 'name'], ''],  // Start with empty filter
                minzoom: 5,
                maxzoom: 14
            });

            ensureTransitLayers(map);
            syncTransitOverlay(map);

            // Update metro region across the whole application using selectLocation
            map.on('click', 'metro-points-click-target', (e) => { 
                const feature = e.features?.[0];
                if (feature?.properties?.name) {
                    selectLocation(feature.properties.name);
                }
            });

            map.on('click', 'metro-areas', (e) => {
                const feature = e.features?.[0];
                if (feature?.properties?.name) {
                    selectLocation(feature.properties.name);
                }
            });

            let activePopup;
            const transitLayers = ['transit-points', 'transit-fill', 'transit-subway', 'transit-light-rail', 'transit-tram'];
            const showFeaturePopup = (e) => {
                if (!e.features?.length) return;

                const feature = e.features[0];
                const properties = feature.properties || {};
                const title = properties.name || properties.railway || 'Feature';
                const details = Object.entries(properties)
                    .map(([key, value]) => `<strong>${key}</strong>: ${value}`)
                    .join('<br/>');

                activePopup?.remove();
                activePopup = new maplibregl.Popup({ closeOnClick: true, closeButton: false })
                    .setLngLat(e.lngLat)
                    .setHTML(`<div style="font-size:12px; line-height:1.3;">${title}<br/>${details}</div>`)
                    .addTo(map);
            };

            transitLayers.forEach((layer) => {
                map.on('click', layer, showFeaturePopup);
                map.on('mouseenter', layer, () => {
                    map.getCanvas().style.cursor = 'pointer';
                });
                map.on('mouseleave', layer, () => {
                    map.getCanvas().style.cursor = '';
                });
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
        isTransitReady = false;
        transitFetchController?.abort();
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