"use strict";

// deepEquals written as an exercise - is this right?

function deepEquals(a, b) {
	if (a === b) {
		return true;
	}
	if (Number.isNaN(a) && Number.isNaN(b)) {
		return true;								// I guess?
	}
	if (typeof a !== "object" || typeof b !== "object") {
		return false;
	}
	// So both are objects...
	if (a === null || b === null) {
		return false;								// We know they're not both null from the test at top
	}
	if (Array.isArray(a) !== Array.isArray(b)) {
		return false;								// Don't consider arrays to equal objects. I guess?
	}
	let a_keys = Object.keys(a);
	let b_keys = Object.keys(b);
	if (a_keys.length !== b_keys.length) {
		return false;
	}
	for (let key of a_keys) {
		if (!Object.prototype.hasOwnProperty.call(b, key)) {		// Object.hasOwn() is too new.
			return false;
		}
		if (!deepEquals(a[key], b[key])) {
			return false;
		}
	}
	return true;
}
