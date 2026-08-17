"use strict";

/*
 * Symmetry status report for Bolo maps.
 *
 * For every .map file in a folder, prints the minimum number of edits
 * (tile changes, object additions/removals) needed to make the map
 * perfectly symmetric under each symmetry mode of the lgm editor
 * (0 = already perfect), the detected perfect symmetry if any, and
 * whether the spawn points share each symmetry.
 *
 * Usage: node symmetry_status.js [folder]
 * Defaults to the folder the script lives in.
 */

let fs = require("fs");
let path = require("path");
let os = require("os");

let lgm_src = path.join(os.homedir(), "github", "lgm", "src");
let bolo_map = require(path.join(lgm_src, "format.js"));
let bolo_sym = require(path.join(lgm_src, "sym.js"));

const MODE_ORDER = ["h", "v", "quad", "rot180", "rot90"];
const MODE_LEGEND = {
	h: "left-right mirror",
	v: "top-bottom mirror",
	quad: "both mirrors",
	rot180: "180 deg rotation",
	rot90: "90 deg rotation",
};

/* ---- status-grid ordering, ported from lgm src/renderer.js ---- */
/* The in-game status display is a 6x3 grid with the two central cells
 * void; spawns have no grid and order top-to-bottom (1x16 column). */
const STATUS_SLOTS = [
	[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0],
	[0, 1], [1, 1],       /* (2,1),(3,1) void */       [4, 1], [5, 1],
	[0, 2], [1, 2], [2, 2], [3, 2], [4, 2], [5, 2],
];
const SPAWN_SLOTS = Array.from({ length: 16 }, (_, i) => [0, i]);

/* Hungarian algorithm (Kuhn-Munkres with potentials), rows n <= cols m.
 * Returns assign[i] = column chosen for row i, minimizing total cost. */
function hungarian(cost) {
	let n = cost.length, m = cost[0].length;
	let u = new Array(n + 1).fill(0), v = new Array(m + 1).fill(0);
	let p = new Array(m + 1).fill(0), way = new Array(m + 1).fill(0);
	for (let i = 1; i <= n; i++) {
		p[0] = i;
		let j0 = 0;
		let minv = new Array(m + 1).fill(Infinity);
		let used = new Array(m + 1).fill(false);
		do {
			used[j0] = true;
			let i0 = p[j0];
			let delta = Infinity, j1 = -1;
			for (let j = 1; j <= m; j++) {
				if (used[j]) continue;
				let cur = cost[i0 - 1][j - 1] - u[i0] - v[j];
				if (cur < minv[j]) { minv[j] = cur; way[j] = j0; }
				if (minv[j] < delta) { delta = minv[j]; j1 = j; }
			}
			for (let j = 0; j <= m; j++) {
				if (used[j]) { u[p[j]] += delta; v[j] -= delta; }
				else minv[j] -= delta;
			}
			j0 = j1;
		} while (p[j0] !== 0);
		do { let j1 = way[j0]; p[j0] = p[j1]; j0 = j1; } while (j0);
	}
	let assign = new Array(n);
	for (let j = 1; j <= m; j++) if (p[j] > 0) assign[p[j] - 1] = j - 1;
	return assign;
}

/* Reorder a list so index order matches the given grid slots intuitively:
 * percentile-rank positions, squared-distance cost, optimal assignment. */
function status_grid_order(list, slots) {
	let n = list.length;
	let idx = [...list.keys()];
	let by_x = idx.slice().sort((a, b) => list[a].x - list[b].x || list[a].y - list[b].y);
	let by_y = idx.slice().sort((a, b) => list[a].y - list[b].y || list[a].x - list[b].x);
	let rx = new Array(n), ry = new Array(n);
	by_x.forEach((i, r) => { rx[i] = r; });
	by_y.forEach((i, r) => { ry[i] = r; });
	let span = Math.max(1, n - 1);
	let gw = Math.max(...slots.map(s => s[0])); /* grid extents for rank scaling */
	let gh = Math.max(...slots.map(s => s[1]));
	let cost = list.map((o, i) => slots.map(([sx, sy]) => {
		let dx = (gw * rx[i]) / span - sx;
		let dy = (gh * ry[i]) / span - sy;
		return dx * dx + dy * dy;
	}));
	let assign = hungarian(cost);
	return idx.sort((a, b) => assign[a] - assign[b]).map(i => list[i]);
}

/* Is the list already in status-grid order? Fewer than two objects is
 * trivially ordered, matching the editor's cmdFixOrder no-op. */
function order_matches(list, slots) {
	if (list.length < 2) return true;
	return status_grid_order(list, slots).every((o, i) => o === list[i]);
}

/* Spawn symmetry for one mode, judged (like detect) about the content
 * box's own axes. Returns null when the mode has no single centre for
 * this content (rot90 with axes of unequal parity). */
function spawn_status(map, mode, s_sum, t_sum) {
	if (mode === "rot90" && (s_sum + t_sum) % 2 !== 0) return null;
	return bolo_sym.spawnsSymmetric(map, mode, s_sum, t_sum);
}

function report_one(file_path) {
	let map = bolo_map.parseMap(new Uint8Array(fs.readFileSync(file_path)));
	let score = bolo_sym.score(map);
	if (!score) return { empty: true };

	let box = bolo_sym.contentBox(map);
	let s_sum = box.minX + box.maxX;
	let t_sum = box.minY + box.maxY;

	let cells = {};
	for (let mode of MODE_ORDER) {
		let flaws = score.perMode[mode];
		if (!isFinite(flaws)) {
			cells[mode] = "n/a";
			continue;
		}
		let sp = spawn_status(map, mode, s_sum, t_sum);
		cells[mode] = String(flaws) + (sp === null ? "" : sp ? "*" : "");
	}

	let detected = bolo_sym.detect(map);
	let summary;
	if (detected) {
		summary = detected.mode + (detected.spawnsSymmetric ? "*" : "");
	} else {
		summary = "none (best " + score.mode + ": " + score.flaws + ")";
	}

	let order = (order_matches(map.bases, STATUS_SLOTS) ? "b" : " ")
		+ (order_matches(map.pills, STATUS_SLOTS) ? "p" : " ")
		+ (order_matches(map.starts, SPAWN_SLOTS) ? "s" : " ");

	return { cells, order, summary };
}

function main() {
	let folder = process.argv[2] || __dirname;
	let files = fs.readdirSync(folder)
		.filter(f => f.toLowerCase().endsWith(".map"))
		.sort((a, b) => a.localeCompare(b));
	if (files.length === 0) {
		console.log("No .map files in " + folder);
		return;
	}

	let name_w = Math.max(4, ...files.map(f => f.length)) + 2;
	let cell_w = 9;
	let header = "Map".padEnd(name_w);
	for (let mode of MODE_ORDER) header += mode.padEnd(cell_w);
	header += "Order".padEnd(7) + "Perfect symmetry";
	console.log(header);
	console.log("-".repeat(header.length));

	for (let file of files) {
		let line = file.padEnd(name_w);
		let row;
		try {
			row = report_one(path.join(folder, file));
		} catch (err) {
			console.log(line + "ERROR: " + err.message);
			continue;
		}
		if (row.empty) {
			console.log(line + "(empty map)");
			continue;
		}
		for (let mode of MODE_ORDER) line += row.cells[mode].padEnd(cell_w);
		line += row.order.padEnd(7) + row.summary;
		console.log(line);
	}

	console.log("");
	console.log("Modes: " + MODE_ORDER.map(m => m + " = " + MODE_LEGEND[m]).join(", "));
	console.log("Cells: minimum edits for perfect symmetry in that mode (0 = already perfect).");
	console.log("       * = spawn points are also symmetric under that mode (spawns are");
	console.log("       otherwise ignored by the symmetry check); no star = spawns break it.");
	console.log("       n/a = mode impossible for this content (rot90 needs axes of equal parity).");
	console.log("Order: which lists are already in the editor's status-grid order (Hungarian");
	console.log("       assignment): b = bases, p = pillboxes, s = spawns. A missing letter");
	console.log("       means that list would be reordered; lists of 0 or 1 count as ordered.");
	console.log("Perfect symmetry: mode detected by the editor, or the closest mode and its edit");
	console.log("       distance when no mode holds perfectly.");
}

main();
