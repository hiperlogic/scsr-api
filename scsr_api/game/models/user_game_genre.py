import json

from mongoengine import signals
from mongoengine.queryset.visitor import Q
from application import db, the_log
from uuid import uuid4
from collections import abc


from user.models.user import UserDB
from game.models.game import GameDB, GameAO 
from game.models.genre import GenreDB, GenreAO

# The UserGameGenre is added only in the scsr creation/update for the game by the user.
# There, the user can add or remove genres from his own list.
class UserGameGenreDB(db.Document):
    """Collection to store how each user set the genre for each game.
        A game may be multi-genre.
    
        Attributes:
            user {UserDB}
            game {GameDB}
            genre {list}

        Methods:
            to_obj

        Action Methods:

        Class/Static Methods:
    """

    external_id = db.StringField(db_field="external_id", required=True) # pylint: disable=no-member
    user = db.ReferenceField(UserDB, db_field="user", required=True) # pylint: disable=no-member
    game = db.ReferenceField(GameDB, db_field="game", required=True) # pylint: disable=no-member
    #unique guarantees the code to occurr only once.
    genre = db.ListField(db.ReferenceField(GenreDB), db_field="genre_list", required=True, unigue=True) # pylint: disable=no-member

    meta = {
        "indexes": [("external_id", "user", "game")]
    }

    def to_obj(self):
        retorno={
            "user": self.user.to_obj(),
            "game": self.game.to_obj(),
            "genre": [genre.to_obj() for genre in self.genre]
        }
        return retorno


    def remove_genre(self,genre):
        """ Removes one genre from the list
                The proper genre object must be provided by the caller.
            Arguments:
                genre {GenreDB} -- The genre
        """
        if(not isinstance(genre,GenreDB)):
            raise TypeError("ERROR: Argument provided is not an object of the type GenreDB. Object provided: "+type(genre))
        if (genre in self.genre):
            if(not hasattr(self, "del_genres")):
                self.del_genres=set()
            self.del_genres.add(genre)

    def add_genre(self, genre):
        """Adds one genre to the user list of genres for the game. Ex: Baldurs Gate is either an RPG and a (sort of) strategy game.
            if the Genre does not exists in the Genre list, it is added, else, it is referenced.
            The proper genre object must be provided by the caller.
        
            
            Arguments:
                genre {GenreDB} -- the genre name.
        """
        if(not isinstance(genre,GenreDB)):
            raise TypeError("ERROR: Argument provided is not an object of the type GenreDB. Object provided: "+type(genre))
        #The method only works with a user and a game
        if(not self.user):
            raise RuntimeError("ERROR: Invalid Object! No User assigned")
        if(not self.game):
            raise RuntimeError("ERROR: Invalid Object! No Game assigned")

        if(not hasattr(self,'new_genres')):
            self.new_genres=set()
        self.new_genres.add(genre)
        pass

    def add_genres(self, genreObjList):
        """ Adds to the game the list of genre objs
        
        Arguments:
            genreObjList {list} -- List containing the genre objects to be added
        """
        for genre in genreObjList:
            #garantees that all objects are genre
            if(not isinstance(genre,GenreDB)):
                raise TypeError("ERROR: Argument provided is not an object of the type GenreDB. Object provided: "+type(genre))

        if(not self.user):
            raise RuntimeError("ERROR: Invalid Object! No User assigned")
        if(not self.game):
            raise RuntimeError("ERROR: Invalid Object! No Game assigned")
        if(not hasattr(self,'new_genres')):
            self.new_genres=set()
        for gn in genreObjList:
            if not gn in self.genre:
                self.new_genres.add(gn)

    @staticmethod
    def get_valid_game(game_data):
        if(not isinstance(game_data,GameDB)):
            raise TypeError("ERROR: Argument provided is not an object of the type GameDB. Object provided: "+type(game_data))
        return UserGameGenreDB.objects.filter(game=game_data,user__live=True) # pylint: disable=no-member

    @classmethod
    def preSave(cls, sender, document, **kwargs):
        """ Prior to saving to the database, the collection is queried to retrieve the pre-data in order to perform the post-save maintenance
        In this case, the data to do maintenance is the genre counting in the game.
        Genres added will be added to the game
        Genres removed will be removed from the game
        Some maintenance:
            Check if there is already an entry with the User and game prior to saving... 
            if there is, check if the current document has id
                if not, then must append
                if does then 
                    if the ids match
                        do the maintenance (we are in the usual flow)
                    if not
                        o-oh! MERGE!!! In doubt... MERGE!
        
        Arguments:
            sender {UserGameGenreDB} -- The sender of the signal
            document {UserGameGenreDB} -- The instance to be saved
        """
        if(document.external_id):
            # There is a document already folks!!!
            # Get the data...
            #no need, we already are doing it via new_genres
            if(hasattr(document,"new_genres")):
                for genre in document.new_genres:
                    # If the genre are not already in the genre list, append
                    if(genre not in document.genre):
                        document.genre.append(genre)
                    else:
                        # game already has it. Need to remove due to post save
                        document.new_genres.remove(genre)
            if(hasattr(document,"del_genres")):
                for genre in document.del_genres:
                    if(genre in document.genre):
                        document.genre.remove(genre)
                    else:
                        #game does not have it! Need to remove due to post save
                        document.del_genres.remove(genre)
        else:
            # It is (supposedly) a new document... let's check?
            doWeHave = cls.objects.filter(user=document.user, game=document.game) # pylint: disable=no-member
            if(doWeHave):
                raise RuntimeError("ERROR: Invalid Object! Trying to create a new UserGameGenresDB data when one already exists. User=%s, Game=%s")
            # Check if game and user are assigned
            if(not document.user):
                raise RuntimeError("ERROR: Invalid Object! No User assigned")
            if(not document.game):
                raise RuntimeError("ERROR: Invalid Object! No Game assigned")
            #new document... Groovy
            document.external_id=str(uuid4())
            if(hasattr(document,"new_genres")):
                for genre in document.new_genres:
                    if(genre not in document.genre):
                        document.genre.append(genre)
            #new document, nothing to remove!

    @classmethod
    def postSave(cls, sender, document, **kwargs):
        """ After saving the genre list the user set for the game, the data is compared to the previous genre list the user had
        The differences will be added/subtracted to the game genreCount
        
        Arguments:
            sender {UserGameGenreDB} -- The sender of the signal
            document {UserGameGenreDB} -- The instance of the document
        """
        if(hasattr(document,"new_genres")):
            GameGenreQuantificationDB.s_add_genres(document.game,document.new_genres)
            """ --- PREVIOUS CODE ---
            while(len(document.new_genres)>0):
                the_genre=document.new_genres.pop()
                document.game.increase_genre(the_genre)
            """
        if(hasattr(document,"del_genres")):
            GameGenreQuantificationDB.s_remove_genres(document.game, document.del_genres)
            """ --- PREVIOUS CODE ---
            while(len(document.del_genres)>0):
                the_genre=document.del_genres.pop()
                res=document.game.decrease_genre(the_genre)
                if(res==0):
                    GamesGenresDB.s_remove_game(the_genre,document.game)
            """
        document.game.save()
        

signals.pre_save.connect(UserGameGenreDB.preSave, sender=UserGameGenreDB)
signals.post_save.connect(UserGameGenreDB.postSave, sender=UserGameGenreDB)

class GameGenreQuantificationDB(db.Document):
    """ Class that quantifies the genres in games. Replaces the field in the GamesDB obj, maintaining decoupling of responsibilities.
        This Element Data is created when the referenced game is available in the system. Meaning, a game suggestion is accepted.
        Attributes:
            game {GameDB}: The primary key, refers to the game in process
            genreCount {DictField}: The quantification field. Constructed in the form {string:value} representing the GenreDB external ID and the number of assignments made.

        Methods:
            to_obj(self): Returns the full representation of the quantification in the form:
                [{"genre":GenreObj, "cited":number_of_citations}]
            __maintenance(self): performs the maintenance of the persisted data, counting the genres assigned to the game
            add_genre(self,genre): Increments the genre in the object or adds it setting to 1. Does not persist the data.
            add_genres(self,genres): Increments the genre in the object or adds it setting to 1. Does not persist the data.
            s_add_genre(game,genre): Increments the genre in the game provided. Persists the data.
            s_add_genres(game,genres): Increments the genres of the list in the game provided. Persists the data.
            remove_genre(self,genre): Decrements the genre in the object. Does not persist the data.
            remove_genres(self,genres): Decrements the genre in the object list. Does not persist the data.
            s_remove_genre(game,genre): Decrements the genre in the game provided. Persists the data.
            s_remove_genres(game,genres): Decrements the genres of the list in the game provided. Persists the data.
                Note: The remove method does not remove the key from the dict if the count reaches 0. This indicates that the genre was once considered for the game and this is a valid information.
        
        Note: All the data are considered to be DB data. The Controller must provide the proper data!
    """

    game = db.ReferenceField(GameDB, db_field="game", required=True, primary_key=True) # pylint: disable=no-member
    genreCount = db.DictField(db_field="genreCount", default={}) # pylint: disable=no-member

    def to_obj(self):
        """ Returns the genres with their respective quantification in a list of dictionaris
        
        Returns:
            List(dict) -- The list of dictionaries with the respective genre and quantification in the form (keys) {'genre','cited'}
        """

        retorno=[{'genre':GenreDB.objects.filter(external_id=key).first(),'cited':self.genreCount[key]} for key in self.genreCount.keys()] # pylint: disable=no-member
        return retorno
    
    def add_genre(self,genre):
        """  method to add a genre to the game referred in the object. The quantification is  updated. Data not persisted.
        
        Arguments:
            genre {GenreDB} -- The GenreDB object to be added
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
        """        
        if(not isinstance(genre,GenreDB)):
            raise TypeError("Argument provided is not of the class GenreDB. Class provided: "+type(genre))
        if(genre.external_id in self.genreCount):
            self.genreCount[genre.external_id]=self.genreCount[genre.external_id]+1
        else:
            self.genreCount[genre.external_id]=1
            GamesGenresDB.s_append_game(genre,self.game)

    def remove_genre(self,genre):
        """  method to remove a genre to the game referred in the object. The quantification is  updated. Data not persisted.
        
        Arguments:
            genre {GenreDB} -- The  GenreDB object to be removed
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
        """        
        if(not isinstance(genre,GenreDB)):
            raise TypeError("Argument provided is not of the class GenreDB. Class provided: "+type(genre))
        if(genre.external_id in self.genreCount):
            self.genreCount[genre.external_id]=self.genreCount[genre.external_id]-1
            if(self.genreCount[genre.external_id]<1):
                self.genreCount[genre.external_id]=0
                GamesGenresDB.s_remove_game(genre,self.game)
    
    def add_genres(self,genres):
        """  method to add the genres in the list to the game referred in the object. The quantification is  updated. Data not persisted.
        
        Arguments:
            genre {List(GenreDB)} -- The list of GenreDB objects to be added
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
        """        
        #validate all
        for genre in genres:
            # Although there is a validation for each genre in the add_genre method, the method do perform changes... 
            # This guarantees that no change is made if there is at least one invalid data.
            if(not isinstance(genre,GenreDB)):
                raise TypeError("Argument provided in list is not of the class GenreDB. Class provided: "+type(genre))
        for genre in genres:
            self.add_genre(genre)

    def remove_genres(self,genres):
        """  method to remove the genres in the list to the game referred in the object. The quantification is  updated. Data not persisted.
        
        Arguments:
            genre {List(GenreDB)} -- The list of GenreDB objects to be removed
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
        """        
        #validate all
        for genre in genres:
            # Although there is a validation for each genre in the add_genre method, the method do perform changes... 
            # This guarantees that no change is made if there is at least one invalid data.
            if(not isinstance(genre,GenreDB)):
                raise TypeError("Argument provided in list is not of the class GenreDB. Class provided: "+type(genre))
        for genre in genres:
            self.remove_genre(genre)
            
    def __update_quantification__(self):
        """ Updates the quantification data for the object.
            TODO: Check if a less constly method is provided by python. This shall cost O(N^2)... luckily there are few genres!
            Raises:
                RuntimeError -- No quantification data found!
        """

        #retrieve all user data for this game
        user_datas=UserGameGenreDB.objects.filter(game=self.game) # pylint: disable=no-member
        if(not user_datas):
            raise RuntimeError("ERROR: Quantification data for the game object not found.")
        new_quant={}
        current_gen_list=set(self.genreCount.keys())
        # DAMN... it is fucking O(n^2)... tenho que rever isso!
        for classification in user_datas:
            for genre in classification.genre:
                if(genre.external_id not in new_quant.keys()):
                    new_quant[genre.external_id]=0
                new_quant[genre.external_id]=new_quant[genre.external_id]+1
        new_gen_list=set(new_quant.keys())
        removed=current_gen_list.difference(new_gen_list)
        added=new_gen_list.difference(current_gen_list)
        #updates the games in genre list.
        for to_del in removed:
            GamesGenresDB.s_remove_game(GenreDB.objects.filter(external_id=to_del).first(),self.game) # pylint: disable=no-member
        for to_add in added:
            GamesGenresDB.s_append_game(GenreDB.objects.filter(external_id=to_add).first(),self.game) # pylint: disable=no-member
        self.genreCount=new_quant
        self.save()


    @staticmethod
    def __s_update_quantification__(the_game):
        """ Updates the quantification data for the desired game
        
        Arguments:
            the_game {GameDB} -- The game to have its quantification updated
        
        Raises:
            TypeError -- The game data is not a valid GameDB object
        
        Returns:
            True if executed.
        """

        if(not isinstance(the_game,GameDB)):
            raise TypeError("Argument provided is not a valid GameDB object. Object provided: "+type(the_game))
        #retrieve the quantification object for the game. Its data will be disregarded.
        to_update=GameGenreQuantificationDB.objects.filter(game=the_game) # pylint: disable=no-member
        to_update.__update_quantification__()
        # No exception raised... returns true!
        return True

    @staticmethod
    def s_add_genre(the_game,genre):
        """ Static method to add a genre assigned to a game. The quantification is updated. Data persisted.
        
        Arguments:
            the_game {GameDB} -- A GameDB Object referring to the game
            genre {GenreDB} -- The GenreDB object to be added
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
            RuntimeError -- Error if no valid quantification exists
        """
        if(not isinstance(the_game,GameDB)):
            raise TypeError("Argument provided is not a valid GameDB object. Object provided: "+type(the_game))
        #seek the game_genre object
        to_save=GameGenreQuantificationDB.objects.filter(game=the_game).first() # pylint: disable=no-member
        if(not to_save):
            raise RuntimeError("There is no data for the Game provided. There should be. Game: "+the_game.external_id)
        to_save.add_genre(genre)
        to_save.save()

    @staticmethod
    def s_add_genres(the_game,genres):
        """ Static method to add a list of genres assigned to a game. The quantification is updated. Data persisted.
        
        Arguments:
            the_game {GameDB} -- A GameDB Object referring to the game
            genres {List (GenreDB)} -- A List of GenreDB Objects to be added
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
            RuntimeError -- Error if no valid quantification exists
        """
        if(not isinstance(the_game,GameDB)):
            raise TypeError("Argument provided is not a valid GameDB object. Object provided: "+type(the_game))
        #seek the game_genre object
        to_save=GameGenreQuantificationDB.objects.filter(game=the_game).first() # pylint: disable=no-member
        if(not to_save):
            raise RuntimeError("There is no data for the Game provided. There should be. Game: "+the_game.external_id)
        to_save.add_genres(genres)
        to_save.save()

    @staticmethod
    def s_remove_genre(the_game,genre):
        """ Static method to remove a genre assigned to a game. The quantification is updated. Data persisted.
        
        Arguments:
            the_game {GameDB} -- A GameDB Object referring to the game
            genre {GenreDB} -- The GenreDB object to be removed
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
            RuntimeError -- Error if no valid quantification exists
        """
        if(not isinstance(the_game,GameDB)):
            raise TypeError("Argument provided is not a valid GameDB object. Object provided: "+type(the_game))
        #seek the game_genre object
        to_save=GameGenreQuantificationDB.objects.filter(game=the_game).first() # pylint: disable=no-member
        if(not to_save):
            raise RuntimeError("There is no data for the Game provided. There should be. Game: "+the_game.external_id)
        to_save.remove_genre(genre)
        to_save.save()

    @staticmethod
    def s_remove_genres(the_game,genres):
        """ Static method to remove a list of genres assigned to a game. The quantification is updated. Data persisted.
        
        Arguments:
            the_game {GameDB} -- A GameDB Object referring to the game
            genres {List (GenreDB)} -- A List of GenreDB Objects to be removed
        
        Raises:
            TypeError -- Error if arguments are not of the provided type
            RuntimeError -- Error if no valid quantification exists
        """

        if(not isinstance(the_game,GameDB)):
            raise TypeError("Argument provided is not a valid GameDB object. Object provided: "+type(the_game))
        #seek the game_genre object
        to_save=GameGenreQuantificationDB.objects.filter(game=the_game).first() # pylint: disable=no-member
        if(not to_save):
            raise RuntimeError("There is no data for the Game provided. There should be. Game: "+the_game.external_id)
        to_save.remove_genres(genres)
        to_save.save()

    @staticmethod
    def s_get_genres(the_game):
        """ Return the genre quantification data for the game.

            Arguments: 
                the_game {GameDB} -- The game data to be assessed
            
            Raises:
                TypeError -- If the argument is not a GameDB object
                RuntimeError -- If a valid GameDB object is provided but no quantification is found
            
            Returns:
            List -- List of dictionaries containing the Genre object and the number of citations of the genre for the object in the form {genre,cited}
        """

        if(not isinstance(the_game,GameDB)):
            raise TypeError("Argument provided is not a valid GameDB object. Object provided: "+type(the_game))
        #seek the game_genre object
        to_retrieve=GameGenreQuantificationDB.objects.filter(game=the_game).first() # pylint: disable=no-member
        if(not to_retrieve):
            raise RuntimeError("There is no data for the Game provided. There should be. Game: "+the_game.external_id)
        return to_retrieve.to_obj()

    @staticmethod
    def s_get_genres_ao(the_game):
        """ Return the genre quantification data for the game.

            Arguments: 
                the_game {GameDB} -- The game data to be assessed
            
            Raises:
                TypeError -- If the argument is not a GameDB object
                RuntimeError -- If a valid GameDB object is provided but no quantification is found
            
            Returns:
            List -- List of dictionaries containing the Genre object and the number of citations of the genre for the object in the form {genre,cited}
        """

        if(not isinstance(the_game,GameDB)):
            raise TypeError("Argument provided is not a valid GameDB object. Object provided: "+type(the_game))
        #seek the game_genre object
        to_retrieve=GameGenreQuantificationDB.objects.filter(game=the_game).first() # pylint: disable=no-member
        if(not to_retrieve):
            raise RuntimeError("There is no data for the Game provided. There should be. Game: "+the_game.external_id)
        return [
            {
                "genre": GenreDB.objects.filter(external_id=key).first().to_obj(), # pylint: disable=no-member
                "cited": to_retrieve.genreCount[key]
            }
            for key in to_retrieve.genreCount.keys()
        ]

class GamesGenresDB(db.Document):
    """ Collection that lists all games classified with the genre.
        Game that have 0 in the genre count must be removed from the list.

        Attributes:
            genre {GenreDB} -- The genre the games are assigned to. It is the primary key
            gamesList {ListField(GameDB)} -- A List of GameDB objects. Not just the references.

        Methods:
            s_append_game(the_genre, game): Adds a game to the genre list
            s_remove_game(the_genre, game): Removes a game to the genre list

        TODO:
            Code the methods to:
                Get the games that has at least one of the genres in a list assigned to them
                Get the games that has all genres specified assigned to them.
    """

    genre = db.ReferenceField(GenreDB, db_field="genre", unique=True, primary_key=True) # pylint: disable=no-member
    gamesList = db.ListField(db.ReferenceField(GameDB), default=[]) # pylint: disable=no-member

    def __repr__(self):
        gameslist=[game.__repr__() for game in self.gamesList]
        return f"{self.genre.name}({self.genre.external_id}): {gameslist}"

    def to_obj(self):
        """ Provides the representation of the data. The genre and the list of objects
            
            Returns:
                Dict -- Dictionary type containing the genre as AO and the list of GameAO objects assigned to the genre
        """

        return GamesGenresAO.from_db(self)

    @staticmethod
    def seek_genre(the_genre):
        """ Returns the object referring to the genre and the list of games assigned to it
        
            Arguments:
                the_genre {GenreDB} -- The genre object to be searched
            
            Raises:
                TypeError -- If the argument is not a valid GenreDB object  
            
            Returns:
                Dict -- The dictionary representing the genre and the games list
        """

        if(not isinstance(the_genre,GenreDB)):
            raise TypeError("Error: the argument provided is not a valid GenreDB object. Object provided: "+type(the_genre))
        GameGenresORM=GamesGenresDB.objects.filter(genre=the_genre).first() # pylint: disable=no-member
        return GameGenresORM

    @staticmethod
    def s_append_game(the_genre,game):
        """ Appends a game to the games list of the genre. Only if not already there.
            
            Arguments:
                the_genre {GenreDB} -- The GenreDB object for the game to be appended to
                game {GameDB} -- The GameDB object to be appended
            
            Raises:
                TypeError -- GenreDB object is not valid
                TypeError -- GameDB object is not valid
                RuntimeError -- No data found for the genre!
        """

        if(not isinstance(the_genre,GenreDB)):
            raise TypeError("Error: the argument provided is not a valid GenreDB object. Object provided: "+type(the_genre))

        if(not isinstance(game,GameDB)):
            raise TypeError("Error: the argument provided is not a valid GameDB object. Object provided: "+type(game))
        GameGenresORM=GamesGenresDB.objects.filter(genre=the_genre).first() # pylint: disable=no-member
        if(not GameGenresORM):
            raise RuntimeError("Error: Data Element not found for the GenreDB: %s in GamesGenresDB collection.",the_genre.external_id)
        if(not (game in GameGenresORM.gamesList)):
            GameGenresORM.gamesList.append(game)
        GameGenresORM.save()
    
    @staticmethod
    def s_remove_game(the_genre, game):
        """ Removes a game from the games list of the genre. Only if there.
            
            Arguments:
                the_genre {GenreDB} -- The GenreDB object for the game to be appended to
                game {GameDB} -- The GameDB object to be appended
            
            Raises:
                TypeError -- GenreDB object is not valid
                TypeError -- GameDB object is not valid
                RuntimeError -- No data found for the genre!
        """
        if(not isinstance(the_genre,GenreDB)):
            raise TypeError("Error: the argument provided is not a valid GenreDB object. Object provided: "+type(the_genre))

        if(not isinstance(game,GenreDB)):
            raise TypeError("Error: the argument provided is not a valid GameDB object. Object provided: "+type(game))
        GameGenresORM=GamesGenresDB.objects.filter(genre=the_genre).first() # pylint: disable=no-member
        if(not GameGenresORM):
            raise RuntimeError("Error: Data Element not found for the GenreDB: %s in GamesGenresDB collection.",the_genre.external_id)
        if(game in GameGenresORM.gamesList):
            GameGenresORM.gamesList.remove(game)
        GameGenresORM.save()

"""Class GamesGenresAO - Application Object of aggregation of games that are assigned to the specific genre
    Attributes:
        genre - the genre
        games - the set of games that had the genre assigned
    Methods:
        add(game): Adds a game to the set
        discard(game): Discards a game from the set
        and(GamesGenresAO): Returns a GamesGenresAO object containing only the games in both lists
        or(GamesGenresAO): Returns a GamesGenresAO object containing all the games in both lists
        xor(GamesGenresAO): Returns a GamesGenresAO object containing only the games not in both lists
        sub(GamesGenresAO): Returns a GamesGenresAO object containing only the games not in the second list
"""

class GamesGenresAO(abc.MutableSet):
    def __init__(self, games=(), genre=None):
        self.games = set(games)

        self.genre = genre

        self.composition = []

    @staticmethod
    def from_db(dbobj):
        if not isinstance(dbobj,GamesGenresDB):
            raise TypeError("ERROR: Argument is not a valid GamesGenresDB object")
        to_return=GamesGenresAO()
        to_return.genre=dbobj.genre.to_obj()
        to_return.games=(game.to_obj() for game in dbobj.gamesList)
        return to_return

    @staticmethod
    def seek_genre(gao):
        if not isinstance(gao,GenreAO):
            raise TypeError("ERROR: Argument is not a valid GenreAO object")
        the_games_genre=GamesGenresDB.seek_genre(gao.__get_persisted__())
        return the_games_genre.to_obj()

    def __contains__(self, game):
        return game in self.games

    def is_composite(self):
        return self.composition

    def __iter__(self):
        return iter(self.games)

    def __len__(self):
        return len(self.games)

    def __or__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno=self.__class__(self.games | other.games, genre=self.genre)
        retorno.composition=["or",(self.composition if self.is_composite else self.genre,
                            other.composition if other.is_composite else other.genre)]
        return retorno

    def __and__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno = self.__class__(self.games & other.games, genre=self.genre)
        retorno.composition=["and",(self.composition if self.is_composite else self.genre,
                            other.composition if other.is_composite else other.genre)]
        return retorno

    def __xor__(self, other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno = self.__class__(self.games ^ other.games, genre=self.genre)
        retorno.composition=["xor",(self.composition if self.is_composite else self.genre,
                            other.composition if other.is_composite else other.genre)]
        return retorno

    def __sub__(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("Operand Type differs. They must be the same")
        retorno = self.__class__(self.games - other.games, genre=self.genre)
        retorno.composition=["difference",(self.composition if self.is_composite else self.genre,
                            other.composition if other.is_composite else other.genre)]
        return retorno

    def add(self, game):
        if not isinstance(game,GameAO):
            raise TypeError("Game is not a valid GameAO object")
        #it uses only ther external_id for the game data.
        self.games.add(game.external_id)

    def discard(self, game):
        if not isinstance(game,GameAO):
            raise TypeError("Game is not a valid GameAO object")
        #it uses only ther external_id for the game data.
        self.games.discard(game.external_id)

    def __json__(self):
        return {game.external_id for game in self.games }

    def __repr__(self):
        base = f"{self.genre}: {self.games}"
        if self.composition:
            base += self.composition
        return base

    def save(self):
        if not isinstance(self.genre,GenreAO):
            raise TypeError("Classificator genre not a valid genreAO object.")
        for game in self.games:
            if not isinstance(game,GameAO):
                raise TypeError("Attempting to save a non GameAO object")
        if self.is_composite():
            raise RuntimeError("Attempting to persist a composite object. Operation not allowed")
        # This data can be save only and if only t is not a composite operand. That means, there were games added to the genre.
        #first: Get the genredb via genre external_id. The genre must exist!
        theElDB=GenreDB.objects.filter(external_id=self.genre.external_id).first() # pylint: disable=no-member
        if not theElDB:
            raise RuntimeError("ERROR: No genre was found in the persistence layer. ID: "+self.genre.external_id)
        #now, get the current db object
        theDB=GamesGenresAO.objects.filter(genre=theElDB).first() # pylint: disable=no-member
        if not theDB:
            raise RuntimeError("ERROR: Related GamegenreMapping not found in the persistent layer.")
        the_games=[game.__get_persisted__() for game in self.games] # pylint: disable=no-member
        theDB.games=the_games
        theDB.save()

    for method in ['clear', 'copy', 'difference', 'difference_update', 'discard', 'intersection', 'intersection_update', 'isdisjoint', 'issubset', 'issuperset', 'pop', 'remove', 'symmetric_difference', 'symmetric_difference_update', 'union', 'update']:
        locals()[method] = (lambda method:lambda self, other=(): getattr(self.games, method)(*((other,) if other else ()) ) ) (method)
