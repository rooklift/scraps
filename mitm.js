"use strict"

const child_process = require("child_process");
const path = require("path");
const readline = require("readline");

// --------------------------------------------------------

let exe = child_process.spawn(
	path.join(__dirname, "bot.exe"),
	[],
	{cwd: __dirname}
)

// --------------------------------------------------------

let exe_scanner = readline.createInterface({
	input: exe.stdout,
	output: undefined,
	terminal: false
});

exe_scanner.on("line", (line) => {
	process.stdout.write(line);
	process.stdout.write("\n");
});

exe_scanner.on("close", () => {
	process.exit(0);
});

// --------------------------------------------------------

let exe_err_scanner = readline.createInterface({
	input: exe.stderr,
	output: undefined,
	terminal: false
});

exe_err_scanner.on("line", (line) => {
	process.stderr.write(line);
	process.stderr.write("\n");
});

// --------------------------------------------------------

let stdin_scanner = readline.createInterface({
	input: process.stdin,
	output: undefined,
	terminal: false
});

stdin_scanner.on("line", (line) => {
	exe.stdin.write(line);
	exe.stdin.write("\n");
});

stdin_scanner.on("close", () => {
	process.exit(0);
});
