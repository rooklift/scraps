"use strict";


const util = require("util");


function log_chain(o, depth = 0) {

	depth += 1;

	// https://nodejs.org/api/util.html#util_util_inspect_object_options

	console.log(depth, util.inspect(o, {showHidden: true, customInspect: false, colors: true}));

	let proto = Object.getPrototypeOf(o);
	if (proto) {
		log_chain(proto, depth);
	}
}



module.exports = log_chain;
