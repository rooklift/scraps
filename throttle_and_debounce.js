function throttle_and_debounce(func, throttle_delay, debounce_delay) {
	let throttle_timeout = null;
	let debounce_timeout = null;
	let last_exec = 0;

	return function(...args) {
		const current_time = Date.now();
		const time_since_last = current_time - last_exec;

		// Clear any existing debounce timer
		clearTimeout(debounce_timeout);

		// Always set a debounce timer to ensure a final update
		debounce_timeout = setTimeout(() => {
			func.apply(this, args);
			last_exec = Date.now();
		}, debounce_delay);

		// If we haven't throttled recently, execute immediately
		if (time_since_last > throttle_delay) {
			func.apply(this, args);
			last_exec = current_time;
		}
	};
}