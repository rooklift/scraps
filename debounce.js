"use strict";

// Implemented after I heard of the concept, I dunno if this is exactly
// what debounce() is supposed to do but it's in the ballpark.

function debounce(f, delay) {
	
	let pending = false;

	return (...args) => {
		if (!pending) {
			pending = true;
			setTimeout(() => {
				f(...args);
				pending = false;
			}, delay);
		}
	};
}



function test(a, b, c) {
	console.log(a, b, c);
}



let foo = debounce(test);

foo(1, 2, 3);
foo(4, 5, 6);
foo(7, 8, 9);
