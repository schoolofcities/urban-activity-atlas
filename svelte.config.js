// import adapter from '@sveltejs/adapter-auto';
import adapter from "@sveltejs/adapter-static"; 
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
// import preprocess from 'svelte-preprocess';

const dev = "production" === "development";


/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	// kit: {
	// 	// adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
	// 	// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
	// 	// See https://svelte.dev/docs/kit/adapters for more information about adapters.
	// 	adapter: adapter()
	// }
	kit: {
		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
		// If your environment is not supported or you settled on a specific environment, switch out the adapter.
		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
		// adapter: adapter()
		
		adapter: adapter({
		    pages: "docs",
		    assets: "docs"
		}),
		paths: {
		    // change below to your repo name
		    base: dev ? "" : "/urban-activity-atlas",
		}
		}
};

export default config;
