"use strict";

let cache = new Map();			// Holds fetch response objects
let inProgress = new Map();		// Holds fetch promises

// Remember multiple callers may get the same promise, which will resolve to
// the same response unless we do something about it. What we need to do is
// ensure each return out of this function adds a .then() which clones it.

function fetcher(url, options = {}) {

	// Must always return a promise.

	if (cache.has(url)) {
		return Promise.resolve(cache.get(url)).then(response => response.clone());
	}

	if (inProgress.has(url)) {
		return inProgress.get(url).then(response => response.clone());
	}

	console.log(`Fetching: ${url}`);

	let fetchPromise = fetch(url, options).then(response => {
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		cache.set(url, response);
		return response;
	}).finally(() => {
		inProgress.delete(url);
	});

	inProgress.set(url, fetchPromise);

	return fetchPromise.then(response => response.clone());
}

module.exports = fetcher;


/* Alternate version, arguably simpler to understand.

let cache = new Map();
let inProgress = new Set();

function fetcher(url, options = {}) {

	if (cache.has(url)) {
		return Promise.resolve(cache.get(url).clone());
	}

	if (!inProgress.has(url)) {
		inProgress.add(url);
		fetch(url, options).then(response => {
			cache.set(url, response);
			inProgress.delete(url);
		});
	}

	let checkCache = (resolve, reject) => {
		if (!inProgress.has(url)) {
			if (cache.has(url)) {
				resolve(cache.get(url).clone());
			} else {
				reject(new Error(`Failed to fetch ${url}`));
			}
		} else {
			setTimeout(() => checkCache(resolve, reject), 100);
		}
	};

	return new Promise((resolve, reject) => {
		setTimeout(() => checkCache(resolve, reject), 100);
	});
}

*/
