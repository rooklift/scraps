function insert_into_comments(s) {

	if (typeof config.comment_box_height !== "number" || config.comment_box_height <= 0) {
		return;
	}

	if (document.activeElement !== comment_drawer.textarea) {
		return;
	}

	// "which you can use to programmatically replace text at the cursor while preserving the undo buffer (edit history)
	// in plain textarea and input elements." -- https://developer.mozilla.org/en-US/docs/Web/API/Document/execCommand

	if (document.execCommand && document.queryCommandSupported && document.queryCommandSupported("insertText")) {
		document.execCommand("insertText", false, s);
	} else {
		let i = comment_drawer.textarea.selectionStart;
		let j = comment_drawer.textarea.selectionEnd;
		comment_drawer.textarea.value = comment_drawer.textarea.value.slice(0, i) + s + comment_drawer.textarea.value.slice(j);
		comment_drawer.textarea.selectionStart = i + 1;
		comment_drawer.textarea.selectionEnd = i + 1;
		hub.commit_comment();							// The "input" event handler doesn't work for direct value setting like this.
	}
}