# Hey there, this is a python music player

# Pardon me for unnecessary use of print statements and messy code,
# I somehow just made it to work lol

import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
import pygame, wave, numpy

from datahandler import *

window = tkinter.Tk()

songpath_file = "Song_data.csv"

class MusicPlayer:

    def __init__(self, window):

        self.btn_fonts = ["⏮️", "▶️", "⏸️", "⏭️", "🔁", "🔂", "🔀"]
        self.cur_songname = None
        self.cur_song_index = -1
        self.songlength = 0
        self.time_played = 0
        self.music_offset = 0
        self.frame = 0

        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.9)

# Music player window
        self.window = window
        self.window.geometry("800x500")
        self.window.title("Personalised Music Player")

# Current playing song container
        self.player_frame = tkinter.Frame(self.window, bg="red")
        self.player_frame.place(relx=0, rely=0, relheight=1, relwidth=.5, anchor="nw")

    # Song information and vfx container
        self.music_frame = tkinter.Frame(self.player_frame, bg="purple")
        self.music_frame.place(relx=0, rely=0, relheight=.6, relwidth=1, anchor="nw")

        # Information
        self.musicinfo_frame = tkinter.Frame(self.music_frame, bg="pink")
        self.musicinfo_frame.pack(side="top", fill="x", anchor="n", padx=20, pady=10)

        self.musictitle_label = tkinter.Label(self.musicinfo_frame, text="Music title")
        self.musictitle_label.pack(side="top", fill="x", anchor="n", padx=10, pady=5)
        self.musicartist_label = tkinter.Label(self.musicinfo_frame, text="Music artist")
        self.musicartist_label.pack(side="top", fill="x", anchor="n", padx=10, pady=5)
        self.musicplaylist_label = tkinter.Label(self.musicinfo_frame, text="Default playlist")
        self.musicplaylist_label.pack(side="top", fill="x", anchor="n", padx=10, pady=5)
        # Vfx
        self.musicvfx_frame = tkinter.Frame(self.music_frame, bg="violet")
        self.musicvfx_frame.pack(side="top", expand=True, fill="both", anchor="n", padx=20, pady=10)
        
        self.vfxframe = tkinter.Canvas(self.musicvfx_frame, bg="white")
        self.vfxframe.pack(side="top", fill="both", anchor="n", padx=5, pady=5)

    # Song controls container
        self.controls_frame = tkinter.Frame(self.player_frame, bg="green")
        self.controls_frame.place(relx=0, rely=.6, relheight=.4, relwidth=1, anchor="nw")

        # Song progess and time
        self.length_control_frame = tkinter.Frame(self.controls_frame)
        self.length_control_frame.place(relx=.5, rely=0, relwidth=1, height=45, anchor="n")
        
        self.progressbar_frame = tkinter.Frame(self.length_control_frame, bg="grey")
        self.progressbar_frame.place(x=0, y=0, relwidth=1, height=25, anchor="nw")
        self.music_progressbar = tkinter.Scale(self.progressbar_frame, orient="horizontal", from_=0, to=100,
                                                showvalue=0, bg="black", command=self.update_progress)
        self.music_progressbar.pack(side="top", fill="x", anchor="n", padx=10)

        self.musicplayed_label = tkinter.Label(self.length_control_frame, text="00:00")
        self.musicplayed_label.place(relx=0, y=25, anchor="nw")
        self.musictime_label = tkinter.Label(self.length_control_frame, text="00:00")
        self.musictime_label.place(relx=1, y=25, anchor="ne")

        # Song button controls
        self.button_control_frame = tkinter.Frame(self.controls_frame)
        self.button_control_frame.place(relx=.5, rely=.6, relwidth=1, height=60, anchor="center")

        self.prevsong_btn = tkinter.Button(self.button_control_frame, text=self.btn_fonts[0], command=lambda: self.skip_prev_next(-1))
        self.prevsong_btn.place(relx=.25, rely=.5, height=30, width=30, anchor="center")
        self.play_pause_btn = tkinter.Button(self.button_control_frame, text=self.btn_fonts[1], command=self.play_pause)
        self.play_pause_btn.place(relx=.5, rely=.5, height=30, width=30, anchor="center")
        self.nextsong_btn = tkinter.Button(self.button_control_frame, text=self.btn_fonts[3], command=lambda: self.skip_prev_next(+1))
        self.nextsong_btn.place(relx=.75, rely=.5, height=30, width=30, anchor="center")

# Container for song lists and options
        self.contents_frame = tkinter.Frame(self.window, bg="blue")
        self.contents_frame.place(relx=.5, rely=0, relheight=1, relwidth=.5, anchor="nw")

    # Container for options
        self.options_frame = tkinter.Frame(self.contents_frame, bg="cyan", height=50)
        self.options_frame.pack(side="top", fill="x", anchor="n")

        import_btn = tkinter.Button(self.options_frame, text="Import", command=self.import_music)
        import_btn.pack(side="left", padx=10, anchor="w")

    # Container for song lists
        self.list_frame = tkinter.Frame(self.contents_frame, bg="yellow")
        self.list_frame.pack(side="top", expand=True, fill="both", anchor="n")

        self.music_list = tkinter.Listbox(self.list_frame, bg="orange")
        self.music_list.pack(side="top", expand=True, fill="both", padx=10, pady=5, anchor="n")
        self.music_list.bind("<<ListboxSelect>>", self.selected_song)

    # Initialization function call
        self.load_music()

# Functions...
    # Initialization functions
    def load_music(self):
        self.songdf = FileIO().read_df_file(songpath_file)
        if(self.songdf.empty):
            FileIO().create_df_file(songpath_file, pandas.Series(['song_name', 'song_path']))
            self.songdf = FileIO().read_df_file(songpath_file)
        else:
            self.songdf = DataManager().validator(self.songdf, 'song_path')
            FileIO().write_df_file(songpath_file, self.songdf)
            self.songlist = self.songdf['song_name']
            self.songpath = self.songdf['song_path']
            self.music_list.delete(0, tkinter.END)
            for i in self.songlist:
                self.music_list.insert(tkinter.END, i)

    # Import function
    def import_music(self):
        music_files = tkinter.filedialog.askopenfilenames(title="Select Music",
            filetypes=[("Audio Files", "*.mp3 *.wav"), ("All Files", "*.*")])
        
        if (music_files):
            music_files = pandas.Series(music_files)
            song_names = FrameLayout().song_from_path(music_files)
            songdataframe = pandas.DataFrame({"song_name":song_names, "song_path":music_files})
            self.songdf = DataManager().union(self.songdf, songdataframe, "song_path")
            FileIO().write_df_file(songpath_file, self.songdf)
            self.load_music()

    # When user clicks a song
    def selected_song(self, event):
        print("A music selected")

    # Check wether a song is selected or not
    def is_song_selected(self):
        self.cur_song_index = self.music_list.curselection()
        if(self.cur_song_index):
            self.cur_song_index = self.cur_song_index[0]
            self.cur_songname = self.music_list.get(self.cur_song_index)
            return True
        else:
            tkinter.messagebox.showinfo("Playback Error!", "Please select a song first!")
            return False

    # Plays song
    def play_song(self):
        for i,j in zip(self.songdf['song_name'], self.songdf['song_path']):
            if(self.cur_songname==i):
                self.cur_songpath = j
        self.music_offset = 0
        pygame.mixer.music.unload()
        pygame.mixer.music.load(self.cur_songpath)
        pygame.mixer.music.play()
        self.initialize_songinfo()
        self.music_progress()
        self.visualize()

    # Initiliaze song info
    def initialize_songinfo(self):
        self.songlength = int(pygame.mixer.Sound(self.cur_songpath).get_length())
        songlengthsecs = int(self.songlength%60)
        songlengthmins = int(self.songlength/60)
        self.music_progressbar.configure(to=self.songlength)

        if(int(songlengthmins/10)==0):
            songlengthmins = "0" + str(songlengthmins)
        if(int(songlengthsecs/10)==0):
            songlengthsecs = "0" + str(songlengthsecs)

        self.musictime_label.configure(text=str(songlengthmins)+":"+str(songlengthsecs))
        self.musictitle_label.configure(text=self.cur_songname)

        file = wave.open(self.cur_songpath, 'rb')
        self.song_parameters = file.getparams()
        self.song_channels, self.song_sampwidth, self.song_samplerate, self.song_samplecount = self.song_parameters[:4]

        raw_data = file.readframes(self.song_samplecount)
        self.songwave_data = numpy.frombuffer(raw_data, dtype=numpy.short)

        self.songwave_data.shape = -1, 2
        self.songwave_data = self.songwave_data.T
    
        self.sample_max = numpy.max(self.songwave_data[0][0:self.song_samplecount]) + 0.0001
        self.sample_min = numpy.min(self.songwave_data[0][0:self.song_samplecount]) - 0.0001

        file.close()

    # Update progressbar and elapsed time label
    def music_progress(self):
        if(pygame.mixer.music.get_busy()):
            self.time_played = int(pygame.mixer.music.get_pos()/1000) + self.music_offset

            time_played_mins = int(self.time_played/60)
            time_played_sec = int(self.time_played%60)

            if(int(time_played_mins/10)==0):
                time_played_mins = "0" + str(time_played_mins)
            if(int(time_played_sec/10)==0):
                time_played_sec = "0" + str(time_played_sec)

            self.musicplayed_label.configure(text=str(time_played_mins)+":"+str(time_played_sec))
            self.music_progressbar.set(self.time_played)
            self.play_pause_btn.config(text=self.btn_fonts[2])
        else:
            self.play_pause_btn.config(text=self.btn_fonts[1])

        self.window.after(1000, self.music_progress)

    # Respond to progressbar change by user
    def update_progress(self, progress):
        progress = int(progress)

        if((progress!=self.time_played)&(self.cur_songname!=None)):
            pygame.mixer.music.play()
            self.music_offset = int(self.music_progressbar.get())
            pygame.mixer.music.set_pos(self.music_offset)

    # Play_pause function
    def play_pause(self):
        playing_song = self.cur_songname

        if(self.is_song_selected()):
            if(playing_song == self.cur_songname):
                if(pygame.mixer.music.get_busy()):
                    pygame.mixer.music.pause()
                    self.play_pause_btn.config(text=self.btn_fonts[1])
                else:
                    if(self.time_played>(self.songlength-3)):
                        self.play_song()
                        self.play_pause_btn.config(text=self.btn_fonts[2])
                    else:
                        pygame.mixer.music.unpause()
                        self.play_pause_btn.config(text=self.btn_fonts[2])
            else:
                self.play_song()
                self.play_pause_btn.config(text=self.btn_fonts[2])

    # Skip to previous or next song
    def skip_prev_next(self, parameter):
        if(self.cur_songname!=None):
            match parameter:
                case -1:
                    if(self.cur_song_index>0):
                        self.cur_song_index += parameter
                case 1:
                    if(self.cur_song_index<(self.music_list.size()-1)):
                        self.cur_song_index += parameter

            self.cur_songname = self.music_list.get(self.cur_song_index)
            self.music_list.activate(self.cur_song_index)
            self.play_song()

    def visualize(self):
        n = 64      # No. of frequency bands (<500 recommended)
        fps = 60    # Frame rate
        
        #freq_bands = [20, 120, 250, 500, 2000, 4000, 6000, 20000]
        #n = len(freq_bands)

        frame_width = self.musicvfx_frame.winfo_width()
        frame_height = self.musicvfx_frame.winfo_height()
        self.vfxframe.delete("all")

        if(pygame.mixer.music.get_busy()):

            if(self.frame<fps):
                self.frame += 1
            else:
                self.frame = 0

            x = self.waveform_data(fps, self.frame, n)
            #x = self.waveform_data2(fps, self.frame, n, freq_bands)
            #x_min = (numpy.min(x))
            #x_max = (numpy.max(x))

            #x_min = 0
            #x_max = 6000000

            #if(x_max==x_min):
            #    x_max += 1e-5

            for i, height in zip(range(n), x):
                height = (height-self.sample_min)/(self.sample_max-self.sample_min)
                #height = (height/x_max)
                
                if (numpy.isnan(height) or height<0):
                    height = 0

                rectangle = [int(i*(frame_width/n)), int(frame_height-10),
                            int((i+1)*(frame_width/n)), int((frame_height-10)-(frame_height*height))]
                self.vfxframe.create_rectangle(rectangle, fill="blue", outline="")

        self.window.after(int(1000/fps), self.visualize)

    def waveform_data(self, fps, frame, number):

        #part = int(self.song_samplerate/fps)
        #sample_area = (self.song_samplerate*self.time_played)+int(part*frame)

        const = 2        
        part = int(self.song_samplerate)
        sample_area = (self.song_samplerate*self.time_played)+int((self.song_samplerate*frame)/fps)

        sample = self.songwave_data[0][sample_area:sample_area+part]

        #fft_sample = numpy.fft.fft(sample)
        #fft_freqs = numpy.fft.fftfreq(len(fft_sample), 1/self.song_samplerate)

        #sample = fft_sample[:len(fft_sample)//2].real

        size = len(sample)
        bars = [0]*number

        if not(size == 0):
            for i in range(number):
                #bars[i] = numpy.nanmean(numpy.abs(sample[int(i*(size/number)):int((i+1)*(size/number))]))
                bars[i] = numpy.nanmean(sample[int(i*(size/number)):int((i+1)*(size/number))])*const
    
        return bars
       
    def waveform_data2(self, fps, frame, number, freq_bands):
        part = int(self.song_samplerate / fps)
        sample_area = int(self.song_samplerate * self.time_played) + int(part * frame)
        sample = self.songwave_data[0][sample_area:sample_area + part]

        if sample.size == 0:
            return numpy.zeros(number)

        fft_sample = numpy.fft.fft(sample)
        fft_freqs = numpy.fft.fftfreq(len(fft_sample), 1 / self.song_samplerate)

        # Use only the positive frequencies and their magnitudes
        positive_freqs = (fft_freqs[:len(fft_freqs)//2])
        magnitudes = numpy.abs(fft_sample[:len(fft_sample)//2])

        # Define the frequency range (20 Hz to 20 kHz)
        min_freq = 20
        max_freq = 20000

        # Create logarithmic bins in the specified range
        #log_bins = numpy.logspace(numpy.log10(min_freq), numpy.log10(max_freq), number + 1)
        #log_bins = numpy.arange(min_freq, max_freq, int(max_freq-(min_freq+number))/number)

        log_bins = freq_bands

        # Prepare bars to hold the mean values
        bars = numpy.zeros(number)

        for i in range(len(log_bins) - 1):
            # Get indices of frequencies in the current log bin
            bin_indices = numpy.where((positive_freqs >= log_bins[i]) & (positive_freqs < log_bins[i + 1]))
            if len(bin_indices[0]) > 0:
                # Compute the mean for the current bin
                bars[i] = numpy.nanmean(magnitudes[bin_indices])  # Change to numpy.nanmax if you prefer max

        return bars
    
MusicPlayer(window)
window.mainloop()

pygame.quit()
