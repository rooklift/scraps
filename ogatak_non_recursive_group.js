	group_at: function(s) {

		let colour = this.state_at(s);

		if (colour === "") {
			return [];
		}

		let touched = Object.create(null);
		touched[s] = true;

		let todo = [s];
		let next = [];

		while (true) {

			if (todo.length === 0) {
				break;
			}

			for (let point of todo) {

				for (let neighbour of this.neighbours(point)) {

					if (touched[neighbour]) {
						continue;
					}

					if (this.state_at(neighbour) === colour) {
						next.push(neighbour);
						touched[neighbour] = true;
					}
				}
			}

			todo = next;
			next = [];
		}

		return Object.keys(touched);
	},