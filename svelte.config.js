// import adapter from '@sveltejs/adapter-auto';
import adapter from "@sveltejs/adapter-static"; 
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
// import preprocess from 'svelte-preprocess';

const dev = process.env.NODE_ENV !== 'production';

const config = {

	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
		    pages: "docs",
		    assets: "docs"
		}),
		paths: {
		    // change below to your repo name for production deployment
		    base: dev ? "" : "/urban-activity-atlas",
		}
	}
};

export default config;
