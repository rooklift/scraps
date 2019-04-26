package main

// This turned out to be super-slow, why?

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/fohristiwhirl/sgf"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	db, err := sql.Open("sqlite3", "./go.db")
	if err != nil {
		panic(err)
	}

	db_files := make(map[string]bool)
	present_files := make(map[string]bool)

	// Make set of all files in the database...

	rows, err := db.Query("SELECT path, filename FROM Games")
	if err != nil {
		panic(err)
	}

	for rows.Next() {
		var path, filename string
		err = rows.Scan(&path, &filename)
		if err != nil {
			panic(err)
		}
		fullpath := filepath.Join(path, filename)
		db_files[fullpath] = true
	}
	rows.Close()

	// Make set of all files in the directory...

	walker := func(fullpath string, info os.FileInfo, err error) error {
		present_files[fullpath] = true
		return nil
	}

	filepath.Walk("archive", walker)

	// Add to DB...

	var additions []string

	for fullpath := range present_files {
		if db_files[fullpath] == false {        		// Not in DB
			additions = append(additions, fullpath)
		}
	}

	sort.Strings(additions)

	fmt.Printf("Adding to database...\n")
	count := 0

	for _, fullpath := range additions {

		path, filename := filepath.Split(fullpath)

		// For compatibility with Python's split(), any trailing slash characters have to be removed...

		if strings.HasSuffix(path, "\\") || strings.HasSuffix(path, "/") {
			path = path[:len(path) - 1]
		}

		dyer, SZ, HA, PB, PW, RE, DT, EV, err := get_info(fullpath)
		if err != nil {
			continue				// e.g. this will trigger on actual directories
		}

		stmt, err := db.Prepare("INSERT INTO Games(path, filename, dyer, SZ, HA, PB, PW, RE, DT, EV)  VALUES(?,?,?,?,?,?,?,?,?,?)")
		if err != nil {
			panic(err)
		}

		res, err := stmt.Exec(path, filename, dyer, SZ, HA, PB, PW, RE, DT, EV)
		if err != nil {
			panic(err)
		}

		_, err = res.LastInsertId()
		if err != nil {
			panic(err)
		}

		fmt.Printf("%s\n", filename)
		count++
	}

	fmt.Printf("%d files added\n", count)

	// Delete from DB...

	var deletions []string

	for fullpath := range db_files {
		if present_files[fullpath] == false {			// Not present on disk
			deletions = append(deletions, fullpath)
		}
	}

	sort.Strings(deletions)

	fmt.Printf("Removing from database...\n")
	count = 0

	for _, fullpath := range deletions {

		path, filename := filepath.Split(fullpath)

		// For compatibility with Python's split(), any trailing \ characters have to be removed...

		if strings.HasSuffix(path, "\\") {
			path = path[:len(path) - 1]
		}

		stmt, err := db.Prepare("DELETE FROM Games WHERE path = ? AND filename = ?")
		if err != nil {
			panic(err)
		}

		res, err := stmt.Exec(path, filename)
		if err != nil {
			panic(err)
		}

		affect, err := res.RowsAffected()
		if err != nil {
			panic(err)
		}

		if affect != 1 {
			fmt.Printf("WARNING: preceding operation affected %d rows\n")
		}

		fmt.Printf("%s\n", filename)
		count++
	}

	fmt.Printf("%d entries removed\n", count)

	// Done.

	db.Close()
}


func get_info(fullpath string) (dyer, SZ, HA, PB, PW, RE, DT, EV string, err error) {

	root, err := sgf.LoadSGFMainLine(fullpath)
	if err != nil {
		return
	}

	dyer = root.Dyer()

	SZ, _ = root.GetValue("SZ")
	if SZ == "" {
		SZ = "19"
	}

	HA, _ = root.GetValue("HA")
	PB, _ = root.GetValue("PB")
	PW, _ = root.GetValue("PW")
	RE, _ = root.GetValue("RE")
	DT, _ = root.GetValue("DT")
	EV, _ = root.GetValue("EV")

	return
}
