	polyglot_book: function(filepath) {

		let book = [];
		AddTreeToBook(this, book);

		let polyglot_entries = [];

		for (let entry of book) {

			let [x1, y1] = XY(entry.move.slice(0, 2));
			let [x2, y2] = XY(entry.move.slice(2, 4));
			let promotion = entry.move.slice(4);

			let move_val = 0;

			// Convert from 0,0 at top left to 0,0 at bottom left
			let fromFile = x1;
			let fromRank = 7 - y1;
			let toFile = x2;
			let toRank = 7 - y2;

			let promotionPiece = 0;
			if (promotion) {
				switch (promotion.toLowerCase()) {
					case "n": promotionPiece = 1; break;
					case "b": promotionPiece = 2; break;
					case "r": promotionPiece = 3; break;
					case "q": promotionPiece = 4; break;
				}
			}

			move_val |= (toFile & 0b111);           // bits 0-2: to file
			move_val |= ((toRank & 0b111) << 3);    // bits 3-5: to rank
			move_val |= ((fromFile & 0b111) << 6);  // bits 6-8: from file
			move_val |= ((fromRank & 0b111) << 9);  // bits 9-11: from rank
			move_val |= ((promotionPiece & 0b111) << 12); // bits 12-14: promotion piece

			move_val = BigInt(move_val);

			polyglot_entries.push((entry.key << 64n) + (move_val << 48n) + (1n << 32n));
		}

		polyglot_entries.sort((a, b) => (a < b) ? -1 : (a > b) ? 1 : 0);

		let fs = require("fs");

		let totalSize = polyglot_entries.length * 16;
		let buffer = Buffer.alloc(totalSize);

		// Write each BigInt to the buffer in big-endian format
		for (let i = 0; i < polyglot_entries.length; i++) {
			let entry = polyglot_entries[i];

			// Calculate the starting position for this entry
			let position = i * 16;

			// Convert BigInt to a Buffer (16 bytes, big-endian)
			let tempBuf = Buffer.alloc(16);

			// BigInt.prototype.toString(16) gives hex representation
			let hexStr = entry.toString(16).padStart(32, "0");

			// Write hex string to buffer in 2-byte chunks
			for (let j = 0; j < 16; j++) {
				let bytePos = j * 2;
				let hexByte = hexStr.substring(bytePos, bytePos + 2);
				let byteVal = parseInt(hexByte, 16) || 0; // Default to 0 if not enough digits
				tempBuf[j] = byteVal;
			}

			// Copy the temporary buffer to the main buffer
			tempBuf.copy(buffer, position);
		}

		// Write the buffer to the file
		fs.writeFileSync(filepath, buffer);
	},