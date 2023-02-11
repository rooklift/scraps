"use strict";

// Note - this JS version is not used now.

const fs = require("fs");
const readline = require("readline");

const config = require("./reload_config.json");

let replay;
try {
	let buf = fs.readFileSync(config.replay);
	replay = JSON.parse(buf);
} catch(err) {
	console.log(err);
	process.exit(1);
}

let scanner = readline.createInterface({
	input: process.stdin,
	output: undefined,
	terminal: false
});

scanner.on("line", (line) => {
	send_next();
});

let i = 0;

function send_next() {
	let output;
	if (replay.actions) {
		output = replay.actions[i++][`player_${config.team}`];
	} else {
		output = replay.steps[++i][config.team].action;		// NOTE: actions are out by 1 on Kaggle, so do ++i not i++
	}
	console.log(JSON.stringify(output));
}
