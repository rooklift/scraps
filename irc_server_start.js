"use strict";

// The start of an IRC server.

const net = require("net");

const SERVER = "127.0.0.1";
const PORT = 6667;


function log(conn, msg) {
	console.log(`${conn.socket.remoteAddress}:${conn.socket.remotePort} (${conn.nick}) ... ${msg}`);
}


function new_connection(socket) {

	let conn = {
		nick: undefined,
		user: undefined,
		socket : socket,
		channels : {},			// e.g. "#starwars" -> true
	}

	log(conn, "CONNECTED");

	function handle_line(data) {

		let tokens = data.toString().split(" ");

		if (tokens[0] === "NICK") {
			if (tokens[1]) {
				irc.set_nick(conn, tokens[1]);
			}
		}

		if (tokens[0] === "USER") {
			if (tokens[1]) {
				irc.set_user(conn, tokens[1]);
			}
		}

		if (tokens[0] === "JOIN") {
			if (tokens[1]) {
				irc.join_channel(conn, tokens[1]);
			}
		}

		if (tokens[0] === "PART") {
			if (tokens[1]) {
				irc.leave_channel(conn, tokens[1]);
			}
		}

		if (tokens[0] === "PRIVMSG") {
			if (tokens[1]) {
				if (conn.channels[tokens[1]]) {
					irc.msg_to_channel(conn, tokens[1], tokens.slice(2).join(" "));
				}
			}
		}
	}

	socket.on("data", (data) => {
		let lines = data.toString().split("\n");
		for (let line of lines) {
			handle_line(line);
		}
	});

	socket.on("close", () => {
		irc.delete_client(conn);
		log(conn, "CONNECTION CLOSED");
	});

	socket.on("error", () => {
		log(conn, "ERROR");
	});
}


function new_channel(chan_name) {

	let channel = {
		users: {},			// nick --> conn object
	};

	channel.add_user = (conn) => {

		if (conn && conn.nick) {

			channel.users[conn.nick] = conn;
			conn.channels[chan_name] = true;

			channel.msg(conn, "JOIN", chan_name);
		}
	}

	channel.delete_user = (conn) => {

		if (conn && conn.nick) {

			channel.msg(conn, "PART", chan_name);

			delete channel.users[conn.nick];
			delete conn.channels[chan_name];
		}
	}

	channel.msg = (conn, type, msg, suppress_to_source) => {

		let s = `:${conn.nick}!${conn.user}@${conn.socket.remoteAddress} ${type} ${msg}\r\n\r\n`

		if (conn && conn.nick && channel.users[conn.nick] && conn.channels[chan_name]) {
			for (let nick of Object.keys(channel.users)) {
				let out_conn = channel.users[nick];
				if (!suppress_to_source || out_conn !== conn) {
					out_conn.socket.write(s);
				}
			}
		}
	};

	return channel;
}


function make_irc() {

	let irc = {};

	irc.all_clients = {};		// nick			-->		conn object
	irc.all_channels = {};		// chan_name	-->		channel object

	irc.new_connection = (socket) => {
		new_connection(socket);
	};

	irc.startup = () => {
		irc.server = net.createServer(irc.new_connection)
		irc.server.listen(PORT, SERVER);
		console.log(`IRC startup on ${SERVER}:${PORT}`);
	};

	irc.set_nick = (conn, new_nick) => {
		if (irc.all_clients[new_nick] === undefined) {
			irc.all_clients[new_nick] = conn;
			conn.nick = new_nick;
		}
	};

	irc.set_user = (conn, new_user) => {
		if (conn && new_user) {
			conn.user = new_user;
		}
	};

	irc.delete_client = (conn) => {
		if (conn && conn.nick) {
			delete irc.all_clients[conn.nick];
			for (let chan_name of Object.keys(conn.channels)) {
				irc.leave_channel(conn, chan_name);
			}
		}
	};

	irc.join_channel = (conn, chan_name) => {

		if (conn && conn.nick && chan_name) {

			if (chan_name.charAt(0) !== "#") {
				chan_name = "#" + chan_name;
			}

			if (irc.all_channels[chan_name] === undefined) {
				irc.all_channels[chan_name] = new_channel(chan_name)
			}

			irc.all_channels[chan_name].add_user(conn);
			log(conn, `joining ${chan_name}`);
		}
	};

	irc.leave_channel = (conn, chan_name) => {

		if (conn && conn.nick && chan_name) {

			if (chan_name.charAt(0) !== "#") {
				chan_name = "#" + chan_name;
			}

			if (irc.all_channels[chan_name] === undefined) {
				return
			}

			irc.all_channels[chan_name].delete_user(conn);
			log(conn, `leaving ${chan_name}`);

			if (Object.keys(irc.all_channels[chan_name].users).length === 0) {
				delete irc.all_channels[chan_name];
				console.log(`Closed channel ${chan_name}`);
			}
		}
	};

	irc.msg_to_channel = (conn, chan_name, msg) => {

		if (conn && conn.nick && chan_name && msg) {

			if (chan_name.charAt(0) !== "#") {
				chan_name = "#" + chan_name;
			}

			if (msg.charAt(0) != ":") {
				msg = ":" + msg;
			}

			let chan = irc.all_channels[chan_name];
			chan.msg(conn, "PRIVMSG", `${chan_name} ${msg}`, true);
		}
	};

	return irc;
};


let irc = make_irc();
irc.startup();
