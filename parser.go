package main

import (
	"regexp"
	"strconv"
	"strings"
)

func ParseNextPage(page string) (next_page string, ok bool) {
	re := regexp.MustCompile("paginate-nextprev.*?\"next\" href=\"/(.*?)\"")
	matches := re.FindAllStringSubmatch(page, -1)
	if matches != nil {
		return matches[0][1], true
	}

	return "", false
}

func ParseFollowing(page string) []string {
	re := regexp.MustCompile("table-person.*?href=\"/(.*?)/\"")
	matches := re.FindAllStringSubmatch(page, -1)
	if matches != nil {
		following := make([]string, len(matches))
		for i, f := range matches {
			following[i] = f[1]
		}
		return following
	}

	return []string{}
}

// This struct represents a movie in the overall letterboxd system.
type Movie struct {
	id       int64
	name     string
	path     string
	avg_rate float64
}

// Represents the rating given by someone to a specific movie.
type Rating struct {
	name string
	rate int8
}

func ParseMoviesWatched(page string) []Rating {
	re := regexp.MustCompile("poster film-poster.*data-target-link=\"/film/(.*?)/\".*rated-(.*?)\"")
	matches := re.FindAllStringSubmatch(page, -1)
	if matches == nil {
		return []Rating{}
	}

	ratings := make([]Rating, len(matches))
	for i, f := range matches {
		rate, _ := strconv.Atoi(f[2])
		ratings[i] = Rating{f[1], int8(rate)}
	}
	return ratings
}

func ParseMovie(page string) (movie Movie, ok bool) {
	// some films don't have average ratings yet and for those the page
	// structure differes. hence we have 2 regex patterns here, one that
	// searches for all details required and one that leaves the rating out.
	//
	// scanning the page twice (only for the movies without rating) is
	// definitely not optimal but for now I am leaving it like this as a more
	// suffisticated parsing mechanism may be needed anyway depending on how
	// the current performs vs the rest of the application.
	base_regex := "(?s)filmData = .*?id: (.*?),.*?name: \"(.*?)\".*?path: \"/film/(.*?)/\""
	re_some := regexp.MustCompile(base_regex)
	re_all := regexp.MustCompile(base_regex + ".*ratingValue\":(.*?),")

	matches := [][]string{}

	has_rating := strings.Index(page, "ratingValue") > 0
	if has_rating {
		matches = re_all.FindAllStringSubmatch(page, -1)
	} else {
		matches = re_some.FindAllStringSubmatch(page, -1)
	}

	if matches == nil {
		return movie, false
	}

	movie.id, _ = strconv.ParseInt(matches[0][1], 10, 64)
	movie.name = matches[0][2]
	movie.path = matches[0][3]

	if has_rating {
		movie.avg_rate, _ = strconv.ParseFloat(matches[0][4], 64)
	}

	// this page keeps the rating in a 0-5 scale whilst we want a 1-10
	movie.avg_rate *= 2

	return movie, true
}
