package main

import (
	"fmt"
	"math/rand"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// How many random picks we'll try before giving up. Tunable.
const max_attempts = 5

// open_file hands the file to whatever Windows has registered as the default
// handler for its type — the same resolution Explorer uses on a double-click.
func open_file(path string) error {
	return exec.Command("rundll32", "url.dll,FileProtocolHandler", path).Start()
}

func main() {
	// Where am I?
	self, err := os.Executable()
	if err != nil {
		fmt.Fprintln(os.Stderr, "could not determine executable path:", err)
		os.Exit(1)
	}
	// Resolve symlinks so the self-comparison below is reliable.
	if resolved, err := filepath.EvalSymlinks(self); err == nil {
		self = resolved
	}

	dir := filepath.Dir(self)

	entries, err := os.ReadDir(dir)
	if err != nil {
		fmt.Fprintln(os.Stderr, "could not read directory:", err)
		os.Exit(1)
	}
	if len(entries) == 0 {
		fmt.Fprintln(os.Stderr, "directory is empty:", dir)
		os.Exit(1)
	}

	// math/rand's global source is auto-seeded as of Go 1.20, so no rand.Seed.
	for attempt := 1; attempt <= max_attempts; attempt++ {
		entry := entries[rand.Intn(len(entries))]

		// Invalid pick: a subdirectory. Retry.
		if entry.IsDir() {
			continue
		}

		full := filepath.Join(dir, entry.Name())
		if resolved, err := filepath.EvalSymlinks(full); err == nil {
			full = resolved
		}

		// Invalid pick: this binary itself (Windows paths are case-insensitive).
		if strings.EqualFold(full, self) {
			continue
		}

		// Valid — open it and quit.
		fmt.Println("Opening:", full)
		if err := open_file(full); err != nil {
			fmt.Fprintln(os.Stderr, "failed to open file:", err)
			os.Exit(1)
		}
		return
	}

	fmt.Fprintf(os.Stderr, "gave up after %d attempts without finding a valid file\n", max_attempts)
	os.Exit(1)
}
