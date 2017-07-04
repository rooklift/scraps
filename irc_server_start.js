"use strict";

// The start of an IRC server...
// See https://modern.ircdocs.horse for useful docs.

const net = require("net");

const SERVER = "127.0.0.1";
const PORT = 6667;

const WELCOME_MSG = ":Welcome to the server!";

// ---------------------------------------------

function is_alphanumeric(str) {
	let code, i, len;

	for (i = 0, len = str.length; i < len; i++) {
		code = str.charCodeAt(i);
		if ((code >= 48 && code <= 57) || (code >= 65 && code <= 90) || (code >= 97 && code <= 122)) {
			continue;
		} else {
			return false;
		}
	}
	return true;	// returns true on empty string
}

function nick_is_legal(str) {
	return str.length > 0 && is_alphanumeric(str);
}

function user_is_legal(str) {
	return str.length > 0 && is_alphanumeric(str);
}

function chan_is_legal(str) {
	if (str.charAt(0) !== "#") {
		return false;
	}
	if (str.length > 1 && is_alphanumeric(str.slice(1))) {
		return true;
	}
	return false;
}

// ---------------------------------------------

function make_irc_server() {

	// Use Object.create(null) when using an object as a map
	// to avoid issued with prototypes.

	let irc = {
		nicks: Object.create(null),
		channels: Object.create(null),
	};

	irc.nick_in_use = (nick) => {
		if (irc.nicks[nick]) {
			return true;
		} else {
			return false;
		}
	};

	irc.remove_conn = (conn) => {
		delete irc.nicks[conn.nick];
	};

	irc.add_conn = (conn) => {
		irc.nicks[conn.nick] = conn;
	};

	irc.get_channel = (chan_name) => {
		return irc.channels[chan_name];		// Can return undefined
	};

	irc.get_or_make_channel = (chan_name) => {
		if (irc.channels[chan_name] === undefined) {
			irc.channels[chan_name] = make_channel(chan_name);
		}
		return irc.channels[chan_name];
	};

	return irc;
}

// ---------------------------------------------

function make_channel(chan_name) {

	let channel = {
		connections: Object.create(null),
	};

	channel.remove_conn = (conn) => {
		channel.raw_send_all(`${conn.id()} PART ${chan_name}`);
		delete channel.connections[conn.nick];
	};

	channel.add_conn = (conn) => {
		channel.connections[conn.nick] = conn;
		channel.raw_send_all(`${conn.id()} JOIN ${chan_name}`);
	};

	channel.raw_send_all = (msg) => {
		for (let nick of Object.keys(channel.connections)) {
			let conn = channel.connections[nick];
			conn.write(msg + "\r\n");
		}
	};

	channel.normal_message = (conn, msg) => {

		if (msg.charAt(0) !== ":") {
			msg = ":" + msg;
		}

		if (msg.length < 2) {
			return;
		}

		for (let nick of Object.keys(channel.connections)) {
			if (nick !== conn.nick) {
				let out_conn = channel.connections[nick];
				out_conn.write(`${conn.id()} PRIVMSG ${chan_name} ${msg}\r\n`);
			}
		}
	};

	channel.name_reply = (conn) => {
		conn.numeric(353, `= ${chan_name} :` + Object.keys(channel.connections).join(" "));
		conn.numeric(366, `${chan_name} :End of NAMES list`);
	};

	return channel;
}

// ---------------------------------------------

function new_connection(socket) {

	let conn = {
		nick: undefined,
		user: undefined,
		socket : socket,
		channels : Object.create(null),		// Use Object.create(null) when using an object as a map
	};

	socket.on("data", (data) => {
		let lines = data.toString().split("\n");
		for (let line of lines) {
			conn.handle_line(line);
		}
	});

	socket.on("close", () => {
		conn.close();
	});

	socket.on("error", () => {});

	conn.close = () => {
		for (let chan_name of Object.keys(conn.channels)) {
			conn.part(chan_name);
		}
	};

	conn.write = (msg) => {
		conn.socket.write(msg);
	};

	conn.numeric = (n, msg) => {

		n = n.toString();

		while (n.length < 3) {
			n = "0" + n;
		}

		let username = conn.nick || "*";

		conn.write(`:${SERVER} ${n} ${username} ${msg}\r\n`);
	};

	conn.id = () => {
		return `:${conn.nick}!${conn.user}@${conn.socket.remoteAddress}`;
	};

	conn.join = (chan_name) => {
		if (chan_is_legal(chan_name)) {
			if (conn.channels[chan_name] === undefined) {
				let channel = irc.get_or_make_channel(chan_name);
				channel.add_conn(conn);
				conn.channels[chan_name] = channel;
				channel.name_reply(conn);
			}
		}
	};

	conn.part = (chan_name) => {
		if (chan_is_legal(chan_name)) {
			let channel = conn.channels[chan_name];
			if (channel) {
				channel.remove_conn(conn);
				delete conn.channels[chan_name];
			}
		}
	};

	conn.handle_line = (msg) => {

		console.log(conn.id() + " ... " + msg);

		let tokens = msg.split(" ");

		// ----------------------------------------------------------- LENGTH 2 -----------------------------------------------------------

		if (tokens.length < 2) {
			return;
		}

		if (tokens[0] === "NICK") {

			let had_nick_already = (conn.nick !== undefined);

			if (nick_is_legal(tokens[1])) {

				if (irc.nick_in_use(tokens[1]) === false) {

					console.log(`${conn.id()} set nick to ${tokens[1]}`);

					irc.remove_conn(conn);
					conn.nick = tokens[1];
					irc.add_conn(conn);

					if (had_nick_already === false && conn.user !== undefined) {		// We just completed registration
						conn.numeric(1, WELCOME_MSG);
					}

				} else {
					conn.numeric(433, ":Nickname is already in use");
				}
			} else {
				conn.numeric(432, ":Erroneus nickname");
			}
		}

		if (tokens[0] === "USER") {
			if (user_is_legal(tokens[1])) {
				if (conn.user === undefined) {
					console.log(`${conn.id()} set username to ${tokens[1]}`);
					conn.user = tokens[1];
					if (conn.nick !== undefined) {										// We just completed registration
						conn.numeric(1, WELCOME_MSG);
					}
				}
			}
		}

		// ----------------------------------------------------------- REG-CHECK ----------------------------------------------------------

		if (conn.nick === undefined || conn.user === undefined) {
			return;
		}

		if (tokens[0] === "JOIN") {

			let chan_name = tokens[1];
			if (chan_name.charAt(0) !== "#") {
				chan_name = "#" + chan_name;
			}

			if (chan_is_legal(chan_name)) {
				conn.join(chan_name);
			}
		}

		if (tokens[0] === "PART") {

			let chan_name = tokens[1];
			if (chan_name.charAt(0) !== "#") {
				chan_name = "#" + chan_name;
			}

			if (chan_is_legal(chan_name)) {
				conn.part(chan_name);
			}
		}

		// ----------------------------------------------------------- LENGTH 3 -----------------------------------------------------------

		if (tokens.length < 3) {
			return;
		}

		if (tokens[0] === "PRIVMSG") {		// FIXME: allow whispers

			let chan_name = tokens[1];
			if (chan_name.charAt(0) !== "#") {
				chan_name = "#" + chan_name;
			}

			let msg = tokens.slice(2).join(" ");

			if (chan_is_legal(chan_name)) {
				let channel = conn.channels[chan_name];
				if (channel) {
					channel.normal_message(conn, msg);
				}
			}
		}
	};
}

// ---------------------------------------------

let irc = make_irc_server();
let server = net.createServer(new_connection);
server.listen(PORT, SERVER);
