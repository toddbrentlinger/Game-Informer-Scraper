
class VideoGame(object):
    def __init__(self, title = "", system = "", releaseDate = "", wikipediaURL = ""):
        self.title = title
        self.system = system
        self.releaseDate = releaseDate
        self.wikipediaURL = wikipediaURL

    def __str__(self):
        return f'{self.title} - {self.system} - {self.releaseDate}'

    def convertToJSON(self):
        return {
            "title": self.title,
            "system": self.system,
            "releaseDate": self.releaseDate,
            "wikipediaURL": self.wikipediaURL
            }