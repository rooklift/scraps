"use strict";

// This is fairly untested code.

const base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

exports.decode = (s) => {

	let inputlength = s.length;

	while (s[inputlength - 1] === "=") {
		inputlength--;
	}

	if (inputlength % 4 === 1) {
		throw "base64 decode(): invalid input length";
	}

	let retlength = Math.floor(inputlength * 0.75);

	let ret = Buffer.alloc(retlength);
	let index = 0;

	let workbits = 0;
	let work = 0;

	for (let i = 0; i < inputlength; i++) {

		let ascii = s.charCodeAt(i);
		let val;

		if (ascii >= 65 && ascii <= 90) {			// A-Z
			val = ascii - 65;
		} else if (ascii >= 97 && ascii <= 122) {	// a-z
			val = ascii - 71;
		} else if (ascii >= 48 && ascii <= 57) {	// 0-9
			val = ascii + 4;
		} else if (ascii === 43) {					//   +
			val = 62;
		} else if (ascii === 47) {					//   /
			val = 63;
		} else {
			throw "base64 decode(): invalid character";
		}

		if (workbits === 0) {
			work = val << 2;
		} else if (workbits === 2) {
			ret[index++] = work + val;
			work = 0;
		} else if (workbits === 4) {
			ret[index++] = work + (val >> 2);
			work = (val & 3) << 6;
		} else if (workbits === 6) {
			ret[index++] = work + (val >> 4);
			work = (val & 15) << 4;
		}

		workbits += 6;
		workbits %= 8;

	}

	if (work) {
		throw "base64 decode(): unexpected end of input";
	}

	return ret;
}


exports.encode = (buf) => {

	if (typeof buf === "string") {
		buf = Buffer.from(buf);
	}

	let retlength = Math.ceil(buf.length / 0.75);

	let ret = Buffer.alloc(retlength);
	let index = 0;
	let padding = "";

	let workbits = 0;
	let work = 0;

	for (let c of buf) {

		if (workbits === 0) {
			ret[index++] = base64_chars.charCodeAt(c >> 2);
			work = (c & 3) << 4;
		} else if (workbits === 2) {
			ret[index++] = base64_chars.charCodeAt(work + (c >> 4));
			work = (c & 15) << 2;
		} else if (workbits === 4) {
			ret[index++] = base64_chars.charCodeAt(work + (c >> 6));
			ret[index++] = base64_chars.charCodeAt(c & 63);
			work = 0;
		}

		workbits += 8;
		workbits %= 6;

	}

	if (workbits > 0) {
		ret[index++] = base64_chars.charCodeAt(work);
		padding = workbits === 2 ? "==" : "=";
	}

	return ret.toString() + padding;
}

