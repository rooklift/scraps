"use strict";

// Implemented after I heard of the concept, I dunno if this is exactly
// what debounce() is supposed to do but it's in the ballpark.

function debounce(f, delay) {
	
	let pending = false;

	return () => {
		if (!pending) {
			pending = true;
			setTimeout(() => {
				f();
				pending = false;
			}, delay);
		}
	};
}



function test() {
	console.log("hi");
}



let foo = debounce(test);

foo();
foo();
foo();
