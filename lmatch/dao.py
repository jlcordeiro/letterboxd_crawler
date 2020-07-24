import pymongo
from pymongo import MongoClient
from lmatch import film


class MovieDao:
    def __init__(self):
        self.client_ = MongoClient()
        self.db_ = self.client_.letterboxd
        self.collection_movies_ = self.db_.movies

    def updateMovie(self, film: film.Film):
        self.collection_movies_.update_one({'_id': film.id},
                                           {'$set': {'_id': film.id,
                                                     'url': film.url,
                                                     'name': film.name,
                                                     'avg_rate': film.avg_rate}},
                                           upsert=True)

    def fetchAllMovies(self, callback):
        for m in self.collection_movies_.find():
            f = film.Film(m['_id'], m['url'], m['name'], m['avg_rate'])
            callback(f)
