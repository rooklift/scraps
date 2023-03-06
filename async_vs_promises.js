"use strict";

function sleep() {
	return new Promise((resolve, reject) => {
		setTimeout(() => resolve(), 1000);
	});
}

async function main1() {
	for (let n = 0; n < 10; n++) {
		console.log(n);
		await sleep();
	}
}

function main2() {
	let ret = Promise.resolve();
	for (let n = 0; n < 10; n++) {
		ret = ret.then(() => {
			console.log(n);
			return sleep();
		});
	}
	return ret;
}

main1().then(() => {
	console.log("done 1");
});

main2().then(() => {
	console.log("done 2");
});

