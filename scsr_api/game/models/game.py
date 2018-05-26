from mongoengine import signals
import json
from application import db, the_log
from game.models.genre import GenreDB, GenreAO
from datetime import datetime
from uuid import uuid4

"""Classes to map the Game representation object in the system to the database.

    Status: In Progress
    TODO: 
        Check if the genres object of the game are being returned in get_genres
        Finish update_data
"""

class GameDB(db.Document):
    """Game Class represents the basic object analyzed. Each scsr must relate to a game object.
    
        Attributes: 
            external_id {String} -- to pass to the client (string)
            year {datetime} -- the year the game was released (datetime component)
            name {String} -- the name of the game (a dictionary element of type lang: name)
                This data is a dictField containing in the key the idiom code and in the data the name of the element in the specified idiom
                Used for Localization
            studio {String} -- The studio name that created the game (string)
            publisher {String} -- The company that published the game (string)
            ##### REMOVED - DECOUPLED TO ITS OWN CLASS
            # genreCount {DictField} -- the statistical user attributed genre for the game.
            # This is a dictionary of the form {'genreId':count}
            #####

        Methods:
            to_obj: Returns a python dict representation of the data

        Action Methods:
            -increase_genre: Increases a genre count (or initializes one with 1) 
                in the game representation
            -decrease_genre: Decreases a genre count (maintaining the lower limit as 0) 
                in the game representation
            -get_genres: Returns a list of the ORM objects of all the genres in game whose count>0
            -update_data: Disregards thecurrent genreCount and generates another one 
                from the UserGameGenre collection

        Class/Static Methods:
            seek_exact_name
            seek_partial_name
            seek_studio

    """

    external_id = db.StringField(db_field="external_id") # pylint: disable=no-member
    year = db.DateTimeField(db_field="year") # pylint: disable=no-member
     # {'lang':'name_in_lang'}
    name = db.DictField(db_field="name", required=True) # pylint: disable=no-member
    studio = db.StringField(db_field="studio") # pylint: disable=no-member
    publisher = db.StringField(db_field="publisher") # pylint: disable=no-member
    date_proposed = db.DateTimeField(db_field="proposed", required=True, default=datetime.utcnow) # pylint: disable=no-member
    date_accepted = db.DateTimeField(db_field="accepted", required=True, default=datetime.utcnow) # pylint: disable=no-member
    active = db.BooleanField(db_field="active", required=True, default=True) # pylint: disable=no-member
    updated = db.DateTimeField(db_field="updated", required=True, default=datetime.utcnow) # pylint: disable=no-member
    
    meta = {
        "indexes": [("external_id", "name", "studio", "publisher", "active")]
    }

    def to_obj(self):
        """Returns the Object as a AO object
        
            Returns:
                GameAO -- the instantiated object as Application Object
        """
        return GameAO.from_GameDB(self)

    def increase_genre(self,genre):
        """ When an user sets the genre for a game, it must be increased (or added)
        
            Arguments:
                genre {GenreDB instance} -- The genre to be added
        """
        from game.models.user_game_genre import GameGenreQuantificationDB
        GameGenreQuantificationDB.s_add_genre(self,genre)
    

    def decrease_genre(self,genre):
        """Decrease the number of times a genre was cited to be assigned to the game
        
        Arguments:
            genre {The genre} -- The genre object assigned to the game
        
        Returns:
            int -- If there is no citations of the genre, 0 is return for maintenance in the GamesGenre data field, 1 otherwise.
        """
        from game.models.user_game_genre import GameGenreQuantificationDB 
        GameGenreQuantificationDB.s_remove_genre(self,genre)

    def get_genres(self):
        """Returns the genres assigned to the game with their respective quantification
        """

        from game.models.user_game_genre import GameGenreQuantificationDB
        GameGenreQuantificationDB.s_get_genres(self)

    def __update_data__(self):
        """
            Updates the genre counts.
            Disregards all of the current data and compute from zero!
            A maintenance method for the game
        """
        from game.models.user_game_genre import GameGenreQuantificationDB
        return GameGenreQuantificationDB.__s_update_quantification__(self) 
    

    @staticmethod
    def seek_exact_name(lang,name):
        """Return the object referent to the game with the name as extacly provided or None
        
        Arguments:
            lang {String} -- Language code for the game name 'pt','en','es','fr',...
            name {String} -- The name to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """

        return GameDB.objects(__raw__={"name."+lang.lower():name}).first() # pylint: disable=no-member

    @staticmethod
    def seek_partial_name(lang,name):
        """Return the object referent to the game with the name containing the text provided
        
        Arguments:
            lang {String} -- Language code for the game name 'pt','en','es','fr',...
            name {String} -- The text to be searched in the game name   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """
        return GameDB.objects(__raw__={"name."+lang.lower():{'$regex':name,'$options':'i'}}) # pylint: disable=no-member

    @staticmethod
    def seek_studio(name):
        """Return the object referent to the game with the studio as extacly provided or None
        
        Arguments:
            name {String} -- The name of the studio to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """
        return GameDB.objects(__raw__={"studio":name})  # pylint: disable=no-member
        
    @staticmethod
    def seek_partial_studio(name):
        """Return the object referent to the game with the studio that contains the text provided or None
        
        Arguments:
            name {String} -- The text part of the studio to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """
        return GameDB.objects(__raw__={"studio":{'$regex':name,'$options':'i'}}) # pylint: disable=no-member

    @staticmethod
    def seek_publisher(name):
        """Return the object referent to the game with the publisher as extacly provided or None
        
        Arguments:
            name {String} -- The name of the publisher to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """

        return GameDB.objects(__raw__={"publisher":name}) # pylint: disable=no-member
        
    @staticmethod
    def seek_partial_publisher(name):
        """Return the object referent to the game with the publisher containing the text provided or None
        
        Arguments:
            name {String} -- The text part of the publisher name to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """
        return GameDB.objects(__raw__={"publisher":{'$regex':name,'$options':'i'}}) # pylint: disable=no-member

    @staticmethod
    def seek_year(the_year):
        """ Seeks the games reported to be published in the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published in the specified year
        """

        dtobj=datetime(year=the_year, month=1, day=1)
        return GameDB.objects(__raw__ = {"year":dtobj}) # pylint: disable=no-member

    @staticmethod
    def seek_post_year(the_year):
        """ Seeks the games reported to be published after the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published after the specified year
        """
        dtobj=datetime(year=the_year, month=1, day=1)
        return GameDB.objects(__raw__ = {"year":{ "$gt": dtobj}}) # pylint: disable=no-member

    @staticmethod
    def seek_pre_year(the_year):
        """ Seeks the games reported to be published prior to the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published prior to the specified year
        """
        dtobj=datetime(year=the_year, month=1, day=1)
        return GameDB.objects(__raw__ = {"year":{"$lt":dtobj}}) # pylint: disable=no-member

    @staticmethod
    def seek_until_year(the_year):
        """ Seeks the games reported to be published until the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published until the specified year
        """
        dtobj=datetime(year=the_year, month=1, day=1)
        return GameDB.objects(__raw__ = {"year":{"$lte":dtobj}}) # pylint: disable=no-member

    @staticmethod
    def seek_from_year(the_year):
        """ Seeks the games reported to be published from the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published from the specified year
        """
        dtobj=datetime(year=the_year, month=1, day=1)
        return GameDB.objects(__raw__ = {"year":{"$lte":dtobj}}) # pylint: disable=no-member

    @staticmethod
    def seek_by_genre(lang,genre):
        """ Seeks the games reported to be classified as the provided genre
        
        Arguments:
            lang {String} -- The language code for the genre specified (ex: 'pt')
            genre {String} -- The genre to be searched
        
        Returns:
            List -- A List of GameDB objects reported to be classified in the specified genre
        TODO: GamesGenres will provide it
        """
        the_gamesAO=GameAO.seek_by_genre(lang,genre)
        the_gamesDB=[el.__get_persisted__() for el in the_gamesAO] # pylint: disable=no-member
        return the_gamesDB

    @staticmethod
    def seek_by_genres_or(lang,genre):
        """ Seeks the games reported to be classified as the provided genre
        
        Arguments:
            lang {String} -- The language code for the genre specified (ex: 'pt')
            genre {String} -- The list genres to be searched
        
        Returns:
            List -- A List of GameDB objects reported to be classified in the specified genres

            TODO: The GamesGenres will provide it!
        """
        pass

    @staticmethod
    def seek_by_genres_and(lang,genre):
        """ Seeks the games reported to be classified as the provided genre
        
        Arguments:
            lang {String} -- The language code for the genre specified (ex: 'pt')
            genre {String} -- The list genres to be searched
        
        Returns:
            List -- A List of GameDB objects reported to be classified in the specified genres

            TODO: The GamesGenres will provide it!
        """
        pass

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ After saving the genre set the external_id
        
        Arguments:
            sender {UserGameGenre} -- The sender of the signal
            document {UserGameGenre} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())
            #it is a new game. calls for a new quantification object
            document.is_new=True

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        """ After saving the genre set the external_id
        
        Arguments:
            sender {UserGameGenre} -- The sender of the signal
            document {UserGameGenre} -- The instance of the document
        """
        if hasattr(document,"is_new"):
            #it is a new game. calls for a new quantification object
            from game.models.user_game_genre import GameGenreQuantificationDB
            newQuant=GameGenreQuantificationDB()
            newQuant.game=document
            #a new game, no genre assigned yet
            newQuant.genreCount={}
            newQuant.save()

    def __repr__(self):
        the_game=f" External_id: {self.external_id}\n Name: {self.name}\n Studio: {self.studio}\n Publisher: {self.publisher}\n Year: {self.year}\n"
        the_game+=f" Active: {self.active}\n Proposed: {self.date_proposed}\n Accepted: {self.date_accepted}\n Updated: {self.updated}"

signals.pre_save.connect(GameDB.pre_save, sender=GameDB)
signals.post_save.connect(GameDB.post_save, sender=GameDB)


class GameAO(object):
    """ Game Application Object - Class to be manipulated by the controller.
    
        Attributes:
            external_id {string} - The data external primary key
            year {datetime} - datetime object of the launch year (can have the full date)
            name {dict} - A dictionary representing the game name in the specific lang. Format: {lang:name_in_lang}. ex: {'en':'Space Invaders'}
            studio {string} - The studio that produced the game
            publisher {string} - the publisher that published the game
            genreCount {Dict} - The quantification of the genres assigned to the game

        Returns:
            [type] -- [description]
    """

    
    #The valid properties to set in an update
    properties=[
            "external_id",
            "year",
            "name",
            "studio",
            "publisher"
        ]

    def __init__(self):
        """The Constructor
            Sets all to none
        """
        self.external_id = None
        self.year = None
        self.name = {}
        self.studio = None
        self.publisher = None
        self.genreCount = []
        self.date_proposed = None
        self.date_accepted = None
        self.active = None

    def __update_data__(self, data):
        if not isinstance(data,GameDB):
            raise TypeError("Error: Argument is not a valid GameDB object.")
        self.external_id = data.external_id
        self.year = data.year
        self.name = data.name
        self.studio = data.studio
        self.publisher = data.publisher
        from game.models.user_game_genre import GameGenreQuantificationDB
        self.genreCount = GameGenreQuantificationDB.s_get_genres_ao(data)
        self.date_proposed = data.date_proposed
        self.date_accepted = data.date_accepted
        self.active = data.active
        self.updated = data.updated

    def __get_persisted__(self):
        if not self.external_id:
            return None
        return GameDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member

    def __repr__(self):
        the_game=f" External_id: {self.external_id}\n Name: {self.name}\n Studio: {self.studio}\n Publisher: {self.publisher}\n Year: {self.year}\n"
        the_game+=f" Active: {self.active}\n Proposed: {self.date_proposed}\n Accepted: {self.date_accepted}\n Updated: {self.updated}"


    @staticmethod
    def from_GameDB(data):
        if not isinstance(data,GameDB):
            raise TypeError("Error: Argument is not a valid GameDB object.")
        retorno=GameAO()
        retorno.external_id = data.external_id
        retorno.year = data.year
        retorno.name = data.name
        retorno.studio = data.studio
        retorno.publisher = data.publisher
        from game.models.user_game_genre import GameGenreQuantificationDB
        retorno.genreCount = GameGenreQuantificationDB.s_get_genres_ao(data)
        retorno.date_proposed = data.date_proposed
        retorno.date_accepted = data.date_accepted
        retorno.active = data.active
        retorno.updated = data.updated
        return retorno

    def to_json(self):
        retorno={
            "external_id" : getattr(self,"external_id",None),
            "year" : getattr(self,"year",None),
            "name" : getattr(self,"name",None),
            "studio" : getattr(self,"studio",None),
            "publisher" : getattr(self,"publisher",None),
            "genreCount" : [{'genre':qtf['genre'].to_json(),'cited':qtf['cited']} for qtf in self.genreCount],
            "date_proposed" : getattr(self,"date_proposed",None),
            "date_accepted" : getattr(self,"date_accepted",None),
            "updated" : getattr(self,"updated",None),
            "active" : getattr(self,"active",None),
        }
        return retorno

    def set_year(self,data):
        if not isinstance(data,datetime):
            raise TypeError("ERROR: date is not a datetime object")
        self.year=data
        if not hasattr(self,"modified"):
            self.modified=set()
        self.modified.add("year")

    def set_name(self,lang, data):
        #TODO: Validate and sanitize data
        self.name[lang]=data
        if not hasattr(self,"modified"):
            self.modified=set()
        self.modified.add("name")

    def set_studio(self,data):
        #TODO: Validate and sanitize data
        self.studio=data
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("studio")

    def set_publisher(self,data):
        #TODO: Validate and sanitize data
        self.publisher=data
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("publisher")

    def wasModified(self):
        return hasattr(self,"modified")

    def save(self):
        to_save=None
        if self.external_id:
            to_save=GameDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member
            if not to_save:
                raise RuntimeError("ERROR: Unmatched object to update. Game not found in DB. External_ID: "+self.external_id)
            if not self.wasModified():
                return
            else:
                to_save.updated = datetime.utcnow()
        else:
            to_save=GameDB()
        self.__delattr__("modified")
        #The name can only be modified via set_name
        to_save.year = self.year
        to_save.name = self.name
        to_save.studio = self.studio
        to_save.publisher = self.publisher
        to_save.active = self.active
        to_save.save()
        self.__update_data__(to_save)

    @staticmethod
    def seek_exact_name(lang,name):
        """Return the object referent to the game with the name as extacly provided or None
            -
            -Arguments:
                lang {str} -- Language code for the game name 'pt','en','es','fr',...
                name {str} -- The name to be searched   
            -
            -Returns:
                GameAO instance -- a GameAO instance with the proper data from the database or None
        """

        return GameDB.seek_exact_name(lang,name).to_obj() 

    @staticmethod
    def seek_partial_name(lang,name):
        """Return the object referent to the game with the name containing the text provided
        
        Arguments:
            lang {String} -- Language code for the game name 'pt','en','es','fr',...
            name {String} -- The text to be searched in the game name   
        
        Returns:
            GameAO instance -- a GameAO instance with the proper data from the database or None
        """
        return GameDB.seek_partial_name(lang,name).to_obj()

    @staticmethod
    def seek_studio(name):
        """Return the object referent to the game with the studio as extacly provided or None
        
        Arguments:
            name {String} -- The name of the studio to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """
        return GameDB. seek_studio(name).to_obj()
        
    @staticmethod
    def seek_partial_studio(name):
        """Return the object referent to the game with the studio that contains the text provided or None
        
        Arguments:
            name {String} -- The text part of the studio to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """
        return [data.to_obj() for data in GameDB.seek_partial_studio(name)]

    @staticmethod
    def seek_publisher(name):
        """Return the object referent to the game with the publisher as extacly provided or None
        
        Arguments:
            name {String} -- The name of the publisher to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """

        return [data.to_obj() for data in GameDB.seek_publisher(name)]
        
    @staticmethod
    def seek_partial_publisher(name):
        """Return the object referent to the game with the publisher containing the text provided or None
        
        Arguments:
            name {String} -- The text part of the publisher name to be searched   
        
        Returns:
            GameDB instance -- a GameDB instance with the proper data from the database or None
        """
        return [data.to_obj() for data in GameDB.seek_partial_publisher(name)]

    @staticmethod
    def seek_year(the_year):
        """ Seeks the games reported to be published in the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published in the specified year
        """
        return [data.to_obj() for data in GameDB.seek_year(the_year)]

    @staticmethod
    def seek_post_year(the_year):
        """ Seeks the games reported to be published after the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published after the specified year
        """
        return [data.to_obj() for data in GameDB.seek_post_year(the_year)]

    @staticmethod
    def seek_pre_year(the_year):
        """ Seeks the games reported to be published prior to the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published prior to the specified year
        """
        return [data.to_obj() for data in GameDB.seek_pre_year(the_year)]

    @staticmethod
    def seek_until_year(the_year):
        """ Seeks the games reported to be published until the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published until the specified year
        """
        return [data.to_obj() for data in GameDB.seek_until_year(the_year)]

    @staticmethod
    def seek_from_year(the_year):
        """ Seeks the games reported to be published from the specified year
        
        Arguments:
            the_year {int} -- An integer object containing the year to be searched
        
        Returns:
            List -- A List of GameDB objects with the games published from the specified year
        """
        return [data.to_obj() for data in GameDB.seek_from_year(the_year)]

    @staticmethod
    def seek_by_genre(lang,genre):
        """ Seeks the games reported to be classified as the provided genre
        
        Arguments:
            lang {String} -- The language code for the genre specified (ex: 'pt')
            genre {String} -- The genre to be searched
        
        Returns:
            List -- A List of GameDB objects reported to be classified in the specified genre
        TODO: GamesGenres will provide it
        """
        the_genre=GenreAO.get_genre(lang,genre)
        from game.models.user_game_genre import GamesGenresAO
        the_games=GamesGenresAO.seek_genre(the_genre)
        return the_games
        
