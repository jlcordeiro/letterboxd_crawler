package main

import (
	"container/list"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"sync"
)

type Profile struct {
	username  string
	following []string
	ratings   []Rating
}

// type that informs the application about what type of page it should be
// looking at. this could be figured out at run time by parsing the page but
// there's no reason to not just keeping track of it.
type PageType int

const (
	MROFILE_PAGE PageType = iota
	WATCHED_PAGE
	FOLLOWING_PAGE
)

type Crawler struct {
	mutex      sync.Mutex
	to_process *List
}

func (c Crawler) enqueueEmptyProfile() {
	c.mutex.Lock()
	defer c.mutex.Unlock()
}

func buildFullUrl(relative_path string) string {
	return "https://letterboxd.com/" + relative_path
}

func downloadProfileSection(profile *Profile, url string, page_type PageType) {
	fmt.Println(":: " + url)

	full_url := buildFullUrl(url)

	// TODO handle errors
	response, _ := http.Get(full_url)
	bytes, _ := ioutil.ReadAll(response.Body)
	response.Body.Close()

	page_content := string(bytes)
	next_page, ok := ParseNextPage(page_content)

	switch page_type {
	case WATCHED_PAGE:
		profile.ratings = append(profile.ratings,
			ParseMoviesWatched(page_content)...)
	case FOLLOWING_PAGE:
		profile.following = append(profile.following,
			ParseFollowing(page_content)...)
	}

	if ok == false {
		return
	}

	downloadProfileSection(profile, next_page, page_type)
	return
}

func crawl(routine_name string, jobs <-chan string, results chan<- string) {
	for username := range jobs {
		profile := Profile{username: username}

		downloadProfileSection(&profile, username+"/following/page/1/", FOLLOWING_PAGE)
		downloadProfileSection(&profile, username+"/films/page/1/", WATCHED_PAGE)

		for _, username_following := range profile.following {
			results <- username_following
		}
	}
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Profile not specified. Closing.")
		return
	}

	const n_routines = 10
	jobs := make(chan string, n_routines)
	outs := make(chan string, 100)

	for t := 0; t < n_routines; t++ {
		goroutine_name := "gr" + strconv.Itoa(t)
		go crawl(goroutine_name, jobs, outs)
	}

	jobs <- os.Args[1]
	for {
		flush_username := <-outs
		jobs <- flush_username
	}
}
