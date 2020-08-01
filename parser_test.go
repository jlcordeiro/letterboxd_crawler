package main

import (
	"io"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
)

func buildMockResponse(w http.ResponseWriter, body_path string) {
	bytes, _ := ioutil.ReadFile(body_path)
	io.WriteString(w, string(bytes))
}

func TestParseNextPage(t *testing.T) {
	tables := []struct {
		path string
		next string
		ok   bool
	}{
		{"jlcordeiro_following_1.html", "jlcordeiro/following/page/2/", true},
		{"jlcordeiro_following_2.html", "", false},
		{"jlcordeiro_watched_1.html", "jlcordeiro/films/page/2/", true},
		{"jlcordeiro_watched_3.html", "jlcordeiro/films/page/4/", true},
		{"jlcordeiro_watched_7.html", "", false},
		{"tommyatlon_watched_1.html", "tommyatlon/films/page/2/", true},
	}

	for _, table := range tables {
		w := httptest.NewRecorder()
		buildMockResponse(w, "./tests/data/"+table.path)
		response := w.Result()
		bytes, _ := ioutil.ReadAll(response.Body)

		result, ok := ParseNextPage(string(bytes))
		if result != table.next || ok != table.ok {
			t.Error(result)
		}

		response.Body.Close()
	}
}

func TestParseFollowing1(t *testing.T) {
	tables := []struct {
		path      string
		following []string
	}{
		{"./tests/data/jlcordeiro_not_following_1.html", []string{}},
		{"./tests/data/jlcordeiro_following_1.html",
			[]string{"dunkeey", "gonfsilva", "crispim",
				"inesqsc", "nihilism", "carsonkims", "o_serkan_o",
				"davidehrlich", "carolina_ab", "nunoabreu", "boppitybunny",
				"apeloeh", "wonderfulcinema", "followtheblind", "jkottke",
				"sandwich", "khoi", "vishnevetsky", "dmoren", "pbones",
				"emanuel", "zkorpi", "inesdelgado", "faitherina", "mpmont"}},
	}

	for _, table := range tables {
		w := httptest.NewRecorder()
		buildMockResponse(w, table.path)
		response := w.Result()
		bytes, _ := ioutil.ReadAll(response.Body)

		result := ParseFollowing(string(bytes))
		if reflect.DeepEqual(result, table.following) == false {
			t.Error(result)
		}

		response.Body.Close()
	}
}

func TestParseMoviesWatched(t *testing.T) {
	tables := []struct {
		path          string
		count_ratings int
		some_ratings  []Rating
	}{
		{"jlcordeiro_watched_1.html", 72, []Rating{}},
		{"jlcordeiro_watched_3.html", 72, []Rating{}},
		{"jlcordeiro_watched_7.html", 27,
			[]Rating{{"suspiria", 7},
				{"pumping-iron", 0},
				{"the-killers", 7}}},
		{"tommyatlon_watched_1.html", 72,
			[]Rating{{"6-underground", 9},
				{"the-equalizer-2", 10},
				{"jurassic-world-fallen-kingdom", 0}}},
		{"jlcordeiro_following_1.html", 0, []Rating{}},
	}

	for _, table := range tables {
		w := httptest.NewRecorder()
		buildMockResponse(w, "./tests/data/"+table.path)
		response := w.Result()
		bytes, _ := ioutil.ReadAll(response.Body)

		result := ParseMoviesWatched(string(bytes))
		if len(result) != table.count_ratings {
			t.Error(len(result))
			t.Error(len(result))
		} else { // correct number of movies
			for _, m := range table.some_ratings {
				for _, n := range result {
					if n.name == m.name && n.rate != m.rate {
						t.Error(result)
					}
				}
			}
		}

		response.Body.Close()
	}
}

func TestParseMovie(t *testing.T) {
	tables := []struct {
		path  string
		ok    bool
		movie Movie
	}{
		{"film_the-way-back-2020.html", true, Movie{458743, "The Way Back", "the-way-back-2020", 6.78}},
		{"film_when-i-rise.html", true, Movie{129797, "When I Rise", "when-i-rise", 0.0}},
		{"jlcordeiro_following_1.html", false, Movie{}},
	}

	for _, table := range tables {
		w := httptest.NewRecorder()
		buildMockResponse(w, "./tests/data/"+table.path)
		response := w.Result()
		bytes, _ := ioutil.ReadAll(response.Body)

		movie, ok := ParseMovie(string(bytes))
		if ok != table.ok || table.movie != movie {
			t.Error(movie)
			t.Error(table.movie)
		}

		response.Body.Close()
	}
}