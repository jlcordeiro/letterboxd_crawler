
class Film:
    """
    Class that contains data related to a movie / film.
    """

    def __init__(self,
                 id: int,
                 url: str,
                 name: str,
                 avg_rate: float):

        self.id = id
        self.url = url
        self.name = name
        self.avg_rate = avg_rate

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return (self.name)

