// file_upload: a tiny single-purpose upload server.
//
// Every request gets a 404 except the one secret path, which serves an
// upload page. Uploads are streamed straight to disk (never held in memory),
// and writing stops if free disk space drops below a safety margin.
//
// Build:  go build file_upload.go
// Run:    ./file_upload -token SECRET -dir /path/to/uploads -addr :8080

package main

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"html"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"time"
)

const check_every = 64 << 20 // re-check free disk space every 64 MB written

var upload_dir string
var secret_path string
var min_free_bytes uint64

func main() {
	addr := flag.String("addr", ":8080", "address to listen on")
	dir := flag.String("dir", "uploads", "directory to save uploads into")
	token := flag.String("token", "", "secret URL token (a random one is generated if empty)")
	min_free_mb := flag.Uint64("min_free_mb", 2048, "stop writing if free disk space falls below this many MB")
	flag.Parse()

	upload_dir = *dir
	min_free_bytes = *min_free_mb << 20

	if err := os.MkdirAll(upload_dir, 0755); err != nil {
		log.Fatalf("cannot create upload directory: %v", err)
	}

	if *token == "" {
		random_bytes := make([]byte, 16)
		if _, err := rand.Read(random_bytes); err != nil {
			log.Fatalf("cannot generate token: %v", err)
		}
		*token = hex.EncodeToString(random_bytes)
		log.Printf("no -token given; generated one. Pass -token %s to keep the same URL after a restart.", *token)
	}
	secret_path = "/" + *token

	log.Printf("saving uploads to %s", upload_dir)
	log.Printf("upload page is at http://<this-server>%s%s", *addr, secret_path)

	server := &http.Server{
		Addr:              *addr,
		Handler:           http.HandlerFunc(handle),
		ReadHeaderTimeout: 30 * time.Second,
		IdleTimeout:       120 * time.Second,
		// No overall read/write timeout: multi-gigabyte uploads can take hours.
	}
	log.Fatal(server.ListenAndServe())
}

func handle(w http.ResponseWriter, r *http.Request) {
	if subtle.ConstantTimeCompare([]byte(r.URL.Path), []byte(secret_path)) != 1 {
		http.NotFound(w, r)
		return
	}
	switch r.Method {
	case http.MethodGet, http.MethodHead:
		serve_page(w)
	case http.MethodPost:
		handle_upload(w, r)
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

func handle_upload(w http.ResponseWriter, r *http.Request) {
	// Refuse up front if the upload obviously won't fit.
	if r.ContentLength > 0 && uint64(r.ContentLength) + min_free_bytes > free_bytes() {
		http.Error(w, "not enough free space on the server for this upload", http.StatusInsufficientStorage)
		return
	}

	reader, err := r.MultipartReader()
	if err != nil {
		http.Error(w, "expected a multipart file upload", http.StatusBadRequest)
		return
	}

	var saved []string
	for {
		part, err := reader.NextPart()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Printf("upload from %s failed while reading: %v", r.RemoteAddr, err)
			http.Error(w, "upload interrupted: " + err.Error(), http.StatusBadRequest)
			return
		}
		if part.FileName() == "" {
			part.Close()
			continue
		}
		final_name, written, err := save_part(part)
		part.Close()
		if err != nil {
			log.Printf("upload of %q from %s failed: %v", part.FileName(), r.RemoteAddr, err)
			http.Error(w, "upload failed: " + err.Error(), http.StatusInternalServerError)
			return
		}
		log.Printf("saved %q (%s) from %s", final_name, human_size(written), r.RemoteAddr)
		saved = append(saved, fmt.Sprintf("%s (%s)", final_name, human_size(written)))
	}

	if len(saved) == 0 {
		http.Error(w, "no file was included in the upload", http.StatusBadRequest)
		return
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	fmt.Fprintf(w, "Saved: %s\n", strings.Join(saved, ", "))
}

// save_part streams one uploaded file to a hidden temporary file, then
// renames it into place only once it has arrived completely.
func save_part(part *multipart.Part) (string, int64, error) {
	name := clean_name(part.FileName())

	tmp, err := os.CreateTemp(upload_dir, ".incoming-*")
	if err != nil {
		return "", 0, err
	}
	tmp_path := tmp.Name()

	written, copy_err := copy_with_space_check(tmp, part)
	close_err := tmp.Close()
	if copy_err == nil {
		copy_err = close_err
	}
	if copy_err != nil {
		os.Remove(tmp_path)
		return "", written, copy_err
	}

	final_name := unique_name(name)
	if err := os.Rename(tmp_path, filepath.Join(upload_dir, final_name)); err != nil {
		os.Remove(tmp_path)
		return "", written, err
	}
	return final_name, written, nil
}

func copy_with_space_check(dst io.Writer, src io.Reader) (int64, error) {
	buf := make([]byte, 1 << 20)
	var total int64
	var since_check int64 = check_every // forces a check before the first write
	for {
		if since_check >= check_every {
			if free_bytes() < min_free_bytes {
				return total, errors.New("server disk is nearly full, so the upload was stopped")
			}
			since_check = 0
		}
		n, read_err := src.Read(buf)
		if n > 0 {
			if _, err := dst.Write(buf[:n]); err != nil {
				return total, err
			}
			total += int64(n)
			since_check += int64(n)
		}
		if read_err == io.EOF {
			return total, nil
		}
		if read_err != nil {
			return total, read_err
		}
	}
}

// clean_name reduces a client-supplied filename to a safe base name.
func clean_name(name string) string {
	name = strings.ReplaceAll(name, "\\", "/")
	name = filepath.Base(name)
	name = strings.Map(func(c rune) rune {
		if c < 32 || c == 127 {
			return -1
		}
		return c
	}, name)
	if name == "" || name == "." || name == ".." || name == "/" {
		name = "upload"
	}
	if strings.HasPrefix(name, ".") {
		name = "_" + name
	}
	return name
}

// unique_name appends " (1)", " (2)" etc. if the name is already taken.
func unique_name(name string) string {
	ext := filepath.Ext(name)
	if strings.HasSuffix(strings.TrimSuffix(name, ext), ".tar") {
		ext = ".tar" + ext
	}
	stem := strings.TrimSuffix(name, ext)
	candidate := name
	for i := 1; ; i++ {
		_, err := os.Stat(filepath.Join(upload_dir, candidate))
		if errors.Is(err, os.ErrNotExist) {
			return candidate
		}
		candidate = fmt.Sprintf("%s (%d)%s", stem, i, ext)
	}
}

func free_bytes() uint64 {
	var st syscall.Statfs_t
	if err := syscall.Statfs(upload_dir, &st); err != nil {
		return 0 // if we can't tell, behave as if the disk is full
	}
	return st.Bavail * uint64(st.Bsize)
}

func human_size(n int64) string {
	units := []string{"B", "KB", "MB", "GB", "TB"}
	value := float64(n)
	i := 0
	for value >= 1024 && i < len(units) - 1 {
		value /= 1024
		i++
	}
	if i == 0 {
		return fmt.Sprintf("%d B", n)
	}
	return fmt.Sprintf("%.1f %s", value, units[i])
}

func serve_page(w http.ResponseWriter) {
	var rows strings.Builder
	entries, err := os.ReadDir(upload_dir)
	if err == nil {
		for _, entry := range entries {
			if entry.IsDir() || strings.HasPrefix(entry.Name(), ".incoming-") {
				continue
			}
			info, err := entry.Info()
			if err != nil {
				continue
			}
			fmt.Fprintf(&rows, "<li>%s <span class=\"size\">%s</span></li>\n",
				html.EscapeString(entry.Name()), human_size(info.Size()))
		}
	}
	file_list := rows.String()
	if file_list == "" {
		file_list = "<li class=\"none\">Nothing yet.</li>"
	}

	page := strings.Replace(page_template, "{{FILES}}", file_list, 1)
	page = strings.Replace(page, "{{FREE}}", human_size(int64(free_bytes())), 1)

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("Referrer-Policy", "no-referrer")
	io.WriteString(w, page)
}

const page_template = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>File Upload</title>
<style>
	body {
		font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
		max-width: 40em;
		margin: 2em auto;
		padding: 0 16px;
		color: #222;
		background: #fafaf8;
		line-height: 1.5;
	}
	h1 {
		font-size: 1.4em;
	}
	.box {
		background: #fff;
		border: 1px solid #ddd;
		border-radius: 6px;
		padding: 1em 1.2em;
		margin: 1em 0;
	}
	button {
		font-size: 1em;
		padding: 0.4em 1.2em;
		margin-top: 0.8em;
	}
	progress {
		width: 100%;
		height: 1.2em;
	}
	#status_list li {
		margin-bottom: 0.8em;
	}
	.size, .note {
		color: #777;
	}
	.none {
		color: #999;
		list-style: none;
	}
</style>
</head>
<body>
<h1>File upload</h1>

<div class="box">
	<form id="upload_form">
		<input type="file" id="file_input" multiple>
		<br>
		<button type="submit" id="upload_button">Upload</button>
	</form>
	<p class="note">Large uploads can be packed into .zip or .tar.gz files first. One big file is fine on a fast, steady connection. On a slow or unreliable one, split it into several parts of a few hundred MB and select them all at once: an interrupted file has to start again from the beginning, but every file marked "done" is safely stored.</p>
	<p class="note">Keep this page open and your computer awake until every file says "done".</p>
</div>

<ul id="status_list"></ul>

<div class="box">
	<strong>Received so far</strong> <span class="note">(server free space: {{FREE}})</span>
	<ul>
{{FILES}}
	</ul>
</div>

<script>
let form = document.getElementById("upload_form");
let input = document.getElementById("file_input");
let button = document.getElementById("upload_button");
let status_list = document.getElementById("status_list");

form.addEventListener("submit", async function (event) {
	event.preventDefault();
	let files = Array.from(input.files);
	if (files.length === 0) {
		return;
	}
	button.disabled = true;
	let failed = [];
	for (let file of files) {
		if (!await upload_one(file)) {
			failed.push(file.name);
		}
	}
	button.disabled = false;
	input.value = "";
	let note = document.createElement("li");
	if (failed.length === 0) {
		note.textContent = "All finished. Reload the page to see the updated list.";
	} else {
		note.textContent = failed.length + " of " + files.length + " did NOT upload: " +
			failed.join(", ") + ". Select just those again and press Upload to retry.";
	}
	status_list.append(note);
});

// Resolves to true if the server confirmed the file was saved, false otherwise.
function upload_one(file) {
	return new Promise(function (resolve) {
		let row = document.createElement("li");
		let label = document.createElement("div");
		let bar = document.createElement("progress");
		bar.max = 100;
		bar.value = 0;
		label.textContent = file.name + ": starting...";
		row.append(label, bar);
		status_list.append(row);

		let xhr = new XMLHttpRequest();
		xhr.open("POST", location.pathname);
		xhr.upload.addEventListener("progress", function (event) {
			if (event.lengthComputable) {
				let percent = event.loaded / event.total * 100;
				bar.value = percent;
				label.textContent = file.name + ": " + percent.toFixed(1) + "% (" +
					format_bytes(event.loaded) + " of " + format_bytes(event.total) + ")";
			}
		});
		xhr.addEventListener("load", function () {
			if (xhr.status === 200) {
				bar.value = 100;
				label.textContent = file.name + ": done";
			} else {
				label.textContent = file.name + ": FAILED - " + xhr.responseText;
			}
			resolve(xhr.status === 200);
		});
		xhr.addEventListener("error", function () {
			label.textContent = file.name + ": FAILED - the connection was lost";
			resolve(false);
		});

		let data = new FormData();
		data.append("file", file);
		xhr.send(data);
	});
}

function format_bytes(n) {
	let units = ["B", "KB", "MB", "GB"];
	let i = 0;
	while (n >= 1024 && i < units.length - 1) {
		n /= 1024;
		i++;
	}
	return n.toFixed(i === 0 ? 0 : 1) + " " + units[i];
}
</script>
</body>
</html>
`
