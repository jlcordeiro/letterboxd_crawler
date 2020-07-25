package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
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

func buildFullUrl(relative_path string) string {
	return "https://letterboxd.com/" + relative_path
}

func crawl(profile *Profile, url string, page_type PageType) {
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

	crawl(profile, next_page, page_type)
}

func downloadProfile(username string) {
	profile := Profile{username: username}

	crawl(&profile, username+"/following/page/1/", FOLLOWING_PAGE)
	crawl(&profile, username+"/films/page/1/", WATCHED_PAGE)

	fmt.Println(profile)
	fmt.Println(len(profile.following))
	fmt.Println(len(profile.ratings))
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Profile not specified. Closing.")
		return
	}

	first_profile := os.Args[1]
	downloadProfile(first_profile)
}
