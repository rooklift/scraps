"use strict";

// Partly written by Claude.

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

module.exports = fetcher;
