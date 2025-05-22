<script>
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
  
	export let path_to_data = '';
	export let title = '';
	export let yticks = [];
	export let y_axis_title = '';
  
	let containerWidth = 750;
	let data = [];
	let days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
	let colors = [
	  '#8DBF2E', '#00A189', '#6FC7EA', '#007FA3', 
	  '#AB1368', '#DC4633', '#F1C500'
	];
  
	// Responsive width adjustment
	onMount(() => {
	  const handleResize = () => {
		const container = document.querySelector('.chart-container');
		if (container) {
		  containerWidth = Math.min(containerWidth, container.parentElement.clientWidth);
		}
	  };
  
	  handleResize();
	  window.addEventListener('resize', handleResize);
  
	  // Load data
	  d3.csv(path_to_data).then(loadedData => {
		data = loadedData.map(d => {
		  const entry = { Hour: +d.Hour };
		  days.forEach(day => entry[day] = +d[day]);
		  return entry;
		});
	  });
  
	  return () => window.removeEventListener('resize', handleResize);
	});
  
	$: if (data.length > 0) {
	  // Set up scales
	  const x = d3.scaleLinear()
		.domain([0, 23])
		.range([50, containerWidth - 20]);
  
	  const y = d3.scaleLinear()
		.domain([d3.min(yticks), d3.max(yticks)])
		.range([360, 40]);
  
	  // Line generator
	  const line = d3.line()
		.x(d => x(d.Hour))
		.y(d => y(d.value));
  
	  // Generate path data for each day
	  const lines = days.map(day => {
		return {
		  day,
		  path: line(data.map(d => ({ Hour: d.Hour, value: d[day] }))),
		  color: colors[days.indexOf(day)]
		};
	  });
  
	  // Generate x axis ticks (every hour)
	  const xTicks = Array.from({ length: 24 }, (_, i) => i);
  
	  // Generate y axis ticks from prop
	  const yTicks = [...yticks];
  
	  // Make these available to the template
	  chartElements = { x, y, lines, xTicks, yTicks };
	}
  
	let chartElements;
  </script>
  
  <div class="chart-container" style="width: {containerWidth}px; height: 450px;">
	<h2>{title}</h2>
	
	<!-- Legend container -->
	<div class="legend-container">
	  {#each chartElements?.lines as line}
		<div class="legend-item">
		  <span class="legend-line" style="border-color: {line.color}"></span>
		  <span class="legend-text">{line.day}</span>
		</div>
	  {/each}
	</div>
	
	<svg width={containerWidth} height="400" viewBox={`0 0 ${containerWidth} 400`}>
	  <!-- Background -->
	  <rect width={containerWidth} height="400" fill="#000" />
  
	  <!-- Y-axis grid lines -->
	  {#each chartElements?.yTicks as tick}
		<line 
		  x1={50} y1={chartElements.y(tick)} 
		  x2={containerWidth - 20} y2={chartElements.y(tick)} 
		  stroke="#333" stroke-width="1" 
		/>
		<text x={45} y={chartElements.y(tick)} fill="#fff" text-anchor="end" dominant-baseline="middle">
		  {tick}
		</text>
	  {/each}
  
	  <!-- X-axis grid lines (hour ticks) -->
	  {#each chartElements?.xTicks as tick}
		<line 
		  x1={chartElements.x(tick)} y1={360} 
		  x2={chartElements.x(tick)} y2={40} 
		  stroke="#333" stroke-width="1" 
		/>
		<text 
		  x={chartElements.x(tick)} y={375} 
		  fill="#fff" text-anchor="middle"
		>
		  {tick}
		</text>
	  {/each}
  
	  <!-- Plot each day's line -->
	  {#each chartElements?.lines as line}
		<path d={line.path} fill="none" stroke={line.color} stroke-width="2" />
	  {/each}

	  {#if y_axis_title}
		<text 
			x={15} 
			y={205} 
			fill="#fff" 
			text-anchor="middle" 
			transform="rotate(-90, 10, 200)"
			class="y-axis-title"
		>
			{y_axis_title}
		</text>
		{/if}
	</svg>
  </div>
  
  <style>
	.chart-container {
	  	background-color: #000;
	  	font-family: RobotoRegular, sans-serif;
		font-weight: normal;
	  	margin: 0 auto;
		margin-top: 30px;
		margin-bottom: 40px;
		text-align: center;
	}
	h2 {
	  	color: #fff;
	  	margin: 0 0 10px 0;
	  	padding: 0;
	 	font-size: 23px;
	  	font-family: TradeGothicBold;
		font-weight: normal;
	}
	text {
	  	font-size: 10px;
	  	font-family: RobotoRegular;
		font-weight: normal;
	}
	.y-axis-title {
		font-size: 14px;
		font-family: RobotoRegular;
	}
	
	.legend-container {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 12px 24px;
		padding: 0 20px;
	}
	
	.legend-item {
		display: flex;
		align-items: center;
		gap: 6px;
	}
	
	.legend-line {
		display: inline-block;
		width: 20px;
		border-bottom: 2px solid;
	}
	
	.legend-text {
		color: #fff;
		font-family: RobotoRegular;
		font-size: 12px;
	}
	
	@media (max-width: 500px) {
		.legend-container {
			gap: 8px 16px;
		}
		.legend-line {
			width: 15px;
		}
		.legend-text {
			font-size: 11px;
		}
	}
  </style>