package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"regexp"
	"strconv"
)

func getMatches(response *http.Response, regex string) [][]string {
	bytes, err := ioutil.ReadAll(response.Body)
	if err != nil {
		return nil
	}

	re := regexp.MustCompile(regex)
	return re.FindAllStringSubmatch(string(bytes), -1)
}

func ParseNextPage(response *http.Response) (next_page string, ok bool) {
	matches := getMatches(response, "paginate-nextprev.*?\"next\" href=\"/(.*?)\"")
	if matches != nil {
		return matches[0][1], true
	}

	return "", false
}

func ParseFollowing(response *http.Response) []string {
	matches := getMatches(response, "table-person.*?href=\"/(.*?)/\"")
	if matches != nil {
		following := make([]string, len(matches))
		for i, f := range matches {
			following[i] = f[1]
		}
		return following
	}

	return []string{}
}

type Rating struct {
	name string
	rate int8
}

func ParseMoviesWatched(response *http.Response) []Rating {
	matches := getMatches(response, "poster film-poster.*data-target-link=\"/film/(.*?)/\".*rated-(.*?)\"")
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

type Movie struct {
	id       int64
	name     string
	path     string
	avg_rate float64
}

func ParseMovie(response *http.Response) (movie Movie, ok bool) {
	matches := getMatches(response, "(?s)filmData = .*?id: (.*?),.*?name: \"(.*?)\".*?path: \"/film/(.*?)/\"")
	//matches := getMatches(response, "(?s)filmData = .*?id: (.*?),.*?name: \"(.*?)\".*?path: \"/film/(.*?)/\".*ratingValue\":(.*?),")
	if matches == nil {
		return movie, false
	}

	id, _ := strconv.Atoi(matches[0][1])
	name := matches[0][2]
	path := matches[0][3]

	movie = Movie{int64(id), name, path, 0.0}

	//movie.avg_rate, _ = strconv.ParseFloat(matches[0][4], 64)

	return movie, true
}

func main() {
	response, _ := http.Get("https://letterboxd.com/film/the-way-back-2020/")
	defer response.Body.Close()
	fmt.Println(ParseMovie(response))
}
