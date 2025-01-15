import os
import pandas

basepath = '/'.join(os.path.abspath(__file__).split('\\')[:(len(os.path.abspath(__file__).split('\\'))-1)]) + '/'

class FrameLayout:      # Convert to or fetch from dataframe
    def __init__(self):
        print("FrameLayout __init__")

    def song_from_path(self, songpath):
        print("Song from path")
        song = []
        for i in songpath:
            j = i.split('/')
            k = j[-1].split('.')
            song.append(k[0])
        return pandas.Series(song)

class DataManager:      # Dataframe operations
    def __init__(self):
        print("DataHandler __init__")

    def validator(self, song_dataframe, path_colname):
        print("Validator")
        validfile_dataframe = pandas.DataFrame(columns=song_dataframe.columns)
        for i in song_dataframe[path_colname]:
            print(i)
            if (os.path.exists(i)):
                j = song_dataframe[song_dataframe[path_colname]==i]
                validfile_dataframe = pandas.concat([validfile_dataframe, j], ignore_index=True)
        return validfile_dataframe


    def union(self, main_dataframe, sub_dataframe, colname):
        print("Union from dataframe")
        if not(main_dataframe.empty):
            for i in sub_dataframe[colname]:
                main_dataframe = main_dataframe[main_dataframe[colname]!=i]
            union_dataframe = pandas.concat([main_dataframe, sub_dataframe], ignore_index=True)
            return union_dataframe
        else:
            return sub_dataframe

class FileIO:           # Read from or write to file
    def __init__(self):
        print("FileIO __init__")

    def create_df_file(self, filename, cols):
        print("Create Dataframe")
        dataframe = pandas.DataFrame(columns=cols)
        try:
            file = open(basepath+filename, 'x')
            dataframe.to_csv(file, index=False)
            file.close()
            return 1
        except:
            return 0

    def read_df_file(self, filename):
        print("Read Dataframe")
        try:
            file = open(basepath+filename, 'r')
            dataframe = pandas.read_csv(file)
            file.close()
            return dataframe
        except:
            return pandas.DataFrame
    
    def write_df_file(self, filename, dataframe):
        print("Write Dataframe")
        file = open(basepath+filename, 'w')
        dataframe.to_csv(file, index=False)
        file.close()



"""
----------------------------Database Schema-----------------------------

songlist layout(dataframe):	//contain path and detail for local song
song_id		song_name	song_path	artist_id

playlist layout(dataframe):	//path for user created playlists
playlist_id	playist_name	playlist_path

playlist(list): 	//contains song id's for given playlist
song_id

artist(dataframe):	//contain different artist's name
artist_id	artist_name

genere layout(dataframe):	//path for all genere playlist file
genre_name	genere_path

genere(list): 		//song belonging to the genere
song_id
---------------------------------------------------------------------

"""