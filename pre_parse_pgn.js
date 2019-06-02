// Pre-parsing means the obliteration of comments and recursive variations.
// I never got going with this, but here are 2 starter functions.

function pre_parse_pgn(buf) {

	let s = new Uint8Array(16);
	let i = 0;

	let push = (v) => {
		if (i === s.length) {
			let new_s = new Uint8Array(s.length * 2);
			for (let n = 0; n < s.length; n++) {
				new_s[n] = s[n];
			}
			s = new_s;
		}
		s[i] = v;
		i++;
	}

	for (let n = 0; n < buf.length; n++) {
		let c = buf[n];

		if (c === 13) {		// Discard \r
			continue;
		}

		push(c);
	}

	return new TextDecoder("utf-8").decode(s.slice(0, i));
}


function pre_parse_pgn(buf) {

	let lines = [];

	let push = (arr) => {
		if (arr.length > 0 && arr[arr.length - 1] === 13) {
			lines.push(arr.slice(0, arr.length - 1));
		} else {
			lines.push(arr);
		}
	}

	let a = 0;

	for (let b = 0; b < buf.length; b++) {
		let c = buf[b];
		if (c === 10) {
			let line = buf.slice(a, b);
			push(line);
			a = b + 1;
		}
	}

	// So lines is now the correct array of Uint8Arrays.
	// We should examine each line and delete unwanted stuff.

	return lines.join("\n");
}