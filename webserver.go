package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const (
	SERVER = "127.0.0.1"
	PORT = 8000
	FILES_DIR = "./files"
)

var KNOWN_EXTENSIONS = map[string]string {
	"css": "text/css",
	"htm": "text/html",
	"html": "text/html",
	"txt": "text/plain",
}

func main() {
	server_and_port := fmt.Sprintf("%s:%d", SERVER, PORT)
	http.HandleFunc("/", main_handler)
	http.ListenAndServe(server_and_port, nil)
}

func send_error(writer http.ResponseWriter, code int, status string) {
	writer.WriteHeader(code)
	writer.Write([]byte(fmt.Sprintf("%d %s", code, status)))
}

func file_from_request(request * http.Request, files_dir string) (infile *os.File, code int, status string, extension string) {

	req_path_clean := strings.Trim(request.URL.Path, "\n\r\t /")

	if strings.Contains(req_path_clean, "..") {		// Safety check. But there is still danger if the files contain a softlink to outside...
		return nil, 403, "Forbidden (path contained '..')", ""
	}

	req_path_list := strings.Split(req_path_clean, "/")
	local_path_list := append([]string{FILES_DIR}, req_path_list...)
	local_filename := filepath.Join(local_path_list...)

	// Try and get fileinfo (so we can check if it's a directory)

	stat, err := os.Stat(local_filename)

	if err != nil {
		if os.IsNotExist(err) {
			return nil, 404, "Not Found", ""
		} else {
			return nil, 500, "Internal Error (os.Stat() failed but not because the file didn't exist)", ""
		}
	}

	// If it is a directory, try using index.html instead...

	if stat.IsDir() {

		local_path_list = append(local_path_list, "index.html")
		local_filename = filepath.Join(local_path_list...)

		stat, err = os.Stat(local_filename)

		if err != nil || stat.IsDir() {			// The 2nd condition means the inferred index.html is itself a directory. Note this test must come 2nd
			return nil, 403, "Forbidden", ""	// otherwise we might cause a panic by calling stat.IsDir() when stat is invalid.
		}
	}

	// Open if possible...

	infile, err = os.Open(local_filename)

	if err != nil {
		return nil, 500, "Internal Error (could not open)", ""
	}

	extension = extension_from_filename(local_filename)

	return infile, 200, "OK", extension
}

func extension_from_filename(filename string) string {
	s := strings.Split(filename, ".")
	if len(s) < 2 {
		return ""
	}
	return s[len(s) - 1]
}

func main_handler(writer http.ResponseWriter, request * http.Request) {

	infile, code, status, extension := file_from_request(request, FILES_DIR)
	defer infile.Close()	// This is safe even if infile is nil

	if code != 200 {
		send_error(writer, code, status)
		return
	}

	buffer := make([]byte, 1024)

	if KNOWN_EXTENSIONS[extension] != "" {
		writer.Header().Add("Content-Type", KNOWN_EXTENSIONS[extension])
	}

	for {

		chars, err := infile.Read(buffer)

		if chars > 0 {
			writer.Write(buffer[0:chars])
		}

		// Note that the first call to writer.Write() triggers a header write, including auto-detecting Content-Type.

		if err != nil {
			return
		}
	}
}

