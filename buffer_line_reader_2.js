"use string";

function new_buffer_line_reader(buf) {
	let reader = Object.create(buffer_line_reader_prototype);
	reader.buf = buf;
	reader.off = 0;
	return reader;
}

let buffer_line_reader_prototype = {

	next() {		// Returns "" at EOF, every other return value has "\n" at the end, except maybe the very last one.

		if (this.off >= this.buf.length) {
			return "";
		}

		let off_initial = this.off;

		for (let i = off_initial; i < this.buf.length; i++) {
			if (this.buf[i] === 10) {
				this.off = i + 1;
				return this.buf.slice(off_initial, i + 1).toString();
			}
		}

		this.off = this.buf.length;
		return this.buf.slice(off_initial).toString();
	}
};



module.exports = new_buffer_line_reader;
