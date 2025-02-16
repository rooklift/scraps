"use strict";

// Written by Claude, mostly.
// A caching system for if multiple components might need to fetch the same URL.
// Note that callers might end up having references to the same promise, but this is apparently fine.

let cache = new Map();			// Holds fetch response objects
let inProgress = new Map();		// Holds fetch promises

function fetcher(url, options = {}) {

	// Must always return a promise.

	if (cache.has(url)) {
		return Promise.resolve(cache.get(url).clone());
	}

	if (inProgress.has(url)) {
		return inProgress.get(url);
	}

	console.log(`Fetching: ${url}`);

	let fetchPromise = fetch(url, options).then(response => {
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		return response;
	}).then(response => {
		inProgress.delete(url);
		cache.set(url, response);
		return response.clone();
	}).catch(error => {
		inProgress.delete(url);
		throw error;
	});

	inProgress.set(url, fetchPromise);
	return fetchPromise;
}

module.exports = fetcher;
