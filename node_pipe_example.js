const spawn = require("child_process").spawn;
const readline = require("readline");

child = spawn("./iterate.exe");

let scanner = readline.createInterface({
	input: child.stdout,
	output: undefined,
	terminal: false
});

scanner.on("line", (line) => {
	process.stdout.write(line + "\n");
});
