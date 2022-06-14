import os
import spotipy
import spotipy.oauth2 as oauth2
import yt_dlp
from youtube_search import YoutubeSearch
import multiprocessing
import tkinter as tk
import tkinter.messagebox as msgbox

# global variables
idClient = ""
secretClient = ""
userName = ""
playlist = ""
txt_id = ""
txt_secret = ""
txt_user = ""
txt_playlist = ""


# function that writes information of each track
def write_tracks(text_file: str, tracks: dict):
    with open(text_file, 'w+', encoding='utf-8') as file_out:
        while True:
            for item in tracks['items']:
                if 'track' in item:
                    track = item['track']
                else:
                    track = item
                try:
                    track_url = track['external_urls']['spotify']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']
                    csv_line = track_name + "," + track_artist + "," + track_url + "\n"
                    try:
                        file_out.write(csv_line)
                    except UnicodeEncodeError:  # Most likely caused by non-English song names
                        print("Track named {} failed due to an encoding error. This is \
                            most likely due to this song having a non-English name.".format(track_name))
                except KeyError:
                    print(u'Skipping track {0} by {1} (local only?)'.format(
                        track['name'], track['artists'][0]['name']))
            # 1 page = 50 results, check if there are more pages
            if tracks['next']:
                tracks = spotify.next(tracks)
            else:
                break


def write_playlist(username: str, playlist_id: str):
    results = spotify.user_playlist(username, playlist_id, fields='tracks,next,name')
    playlist_name = results['name']
    text_file = u'{0}.txt'.format(playlist_name, ok='-_()[]{}')
    print(u'Writing {0} tracks to {1}.'.format(results['tracks']['total'], text_file))
    tracks = results['tracks']
    write_tracks(text_file, tracks)
    return playlist_name


def find_and_download_songs(reference_file: str):
    TOTAL_ATTEMPTS = 10
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            temp = line.split(",")
            name, artist = temp[0], temp[1]
            text_to_search = artist + " - " + name
            best_url = None
            attempts_left = TOTAL_ATTEMPTS
            while attempts_left > 0:
                try:
                    results_list = YoutubeSearch(text_to_search, max_results=1).to_dict()
                    best_url = "https://www.youtube.com{}".format(results_list[0]['url_suffix'])
                    break
                except IndexError:
                    attempts_left -= 1
                    print("No valid URLs found for {}, trying again ({} attempts left).".format(
                        text_to_search, attempts_left))
            if best_url is None:
                print("No valid URLs found for {}, skipping track.".format(text_to_search))
                continue
            # Run you-get to fetch and download the link's audio
            print("Initiating download for {}.".format(text_to_search))
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([best_url])


def multicore_find_and_download_songs(reference_file: str, cpu_count: int):
    lines = []
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            lines.append(line)
    number_of_songs = len(lines)
    songs_per_cpu = number_of_songs // cpu_count
    extra_songs = number_of_songs - (cpu_count * songs_per_cpu)
    cpu_count_list = []
    for cpu in range(cpu_count):
        songs = songs_per_cpu
        if cpu < extra_songs:
            songs = songs + 1
        cpu_count_list.append(songs)
    index = 0
    file_segments = []
    for cpu in cpu_count_list:
        right = cpu + index
        segment = lines[index:right]
        index = index + cpu
        file_segments.append(segment)
    processes = []
    segment_index = 0
    for segment in file_segments:
        p = multiprocessing.Process(target=multicore_handler, args=(segment, segment_index,))
        processes.append(p)
        segment_index = segment_index + 1
    for p in processes:
        p.start()
    for p in processes:
        p.join()


def multicore_handler(reference_list: list, segment_index: int):
    reference_filename = "{}.txt".format(segment_index)
    with open(reference_filename, 'w+', encoding='utf-8') as file_out:
        for line in reference_list:
            file_out.write(line)
    find_and_download_songs(reference_filename)
    if os.path.exists(reference_filename):
        os.remove(reference_filename)


def enable_multicore(autoenable=False, maxcores=None, buffercores=1):
    native_cpu_count = multiprocessing.cpu_count() - buffercores
    if autoenable:
        if maxcores:
            if maxcores <= native_cpu_count:
                return maxcores
            else:
                print("Too many cores requested, single core operation fallback")
                return 1
        return multiprocessing.cpu_count() - 1
    multicore_query = input("Enable multiprocessing (Y or N): ")
    if multicore_query not in ["Y", "y", "Yes", "YES", "YEs", 'yes']:
        return 1
    core_count_query = int(input("Max core count (0 for allcores): "))
    if core_count_query == 0:
        return native_cpu_count
    if core_count_query <= native_cpu_count:
        return core_count_query
    else:
        print("Too many cores requested, single core operation fallback")
        return 1


class Window(tk.Tk):
    def __init__(self):
        global txt_id
        global txt_user
        global txt_playlist
        global txt_secret

        super().__init__()
        self.geometry("500x500")
        self.title("Spotify To MP3 - Ema")
        self.resizable(False, False)
        self.config(background="darkslategray")
        self.main_title = tk.Label(text="Spotify to Mp3", font=("Verdana", 14), bg="#81b71a", fg="black",
                                   width="500", height="2")
        self.main_title.pack()

        self.label_text = tk.StringVar()
        self.label_text.set("Client ID: ")
        self.name_text = tk.StringVar()
        self.label = tk.Label(self, textvar=self.label_text, bg="aquamarine", font=("Verdana", 10))
        self.label.pack(expand=0, padx=10, pady=10, anchor="w")
        self.name_entry = tk.Entry(self, textvar=self.name_text, font=("Verdana", 8))
        self.name_entry.insert(0, txt_id)
        self.name_entry.pack(fill=tk.BOTH, expand=0, padx=30, pady=10)

        self.label_client_secret_text = tk.StringVar()
        self.label_client_secret_text.set("Client Secret: ")
        self.name_clientSecret_text = tk.StringVar()
        self.label_client_secret = tk.Label(self, textvar=self.label_client_secret_text,
                                            bg="aquamarine", font=("Verdana", 10))
        self.label_client_secret.pack(expand=0, padx=10, pady=10, anchor="w")
        self.name_clientSecret_text_entry = tk.Entry(self, textvar=self.name_clientSecret_text, font=("Verdana", 8))
        self.name_clientSecret_text_entry.insert(0, txt_secret)
        self.name_clientSecret_text_entry.pack(fill=tk.BOTH, expand=0, padx=30, pady=10)

        self.label_client_name_text = tk.StringVar()
        self.label_client_name_text.set("UserName(numero): ")
        self.name_clientName_text = tk.StringVar()
        self.label_client_name = tk.Label(self, textvar=self.label_client_name_text,
                                          bg="aquamarine", font=("Verdana", 10))
        self.label_client_name.pack(expand=0, padx=10, pady=10, anchor="w")
        self.name_clientName_text_entry = tk.Entry(self, textvar=self.name_clientName_text, font=("Verdana", 8))
        self.name_clientName_text_entry.insert(0, txt_user)
        self.name_clientName_text_entry.pack(fill=tk.BOTH, expand=0, padx=30, pady=10)

        self.label_client_playlist_text = tk.StringVar()
        self.label_client_playlist_text.set("Playlist Url(solo codigo): ")
        self.name_clientPlaylist_text = tk.StringVar()
        self.label_client_playlist = tk.Label(self, textvar=self.label_client_playlist_text,
                                              bg="aquamarine", font=("Verdana", 10))
        self.label_client_playlist.pack(expand=0, padx=10, pady=10, anchor="w")
        self.name_clientPlaylist_text_entry = tk.Entry(self, textvar=self.name_clientPlaylist_text, font=("Verdana", 8))
        self.name_clientPlaylist_text_entry.insert(0, txt_playlist)
        self.name_clientPlaylist_text_entry.pack(fill=tk.BOTH, expand=0, padx=30, pady=10)

        # Buttons
        submit_button = tk.Button(self, text="Descargar", command=self.download, font=("Verdana", 10), bg="cadetblue")
        submit_button.pack(side=tk.LEFT, padx=(40, 0), pady=(0, 20))

        goodbye_button = tk.Button(self, text="Salir", command=self.say_goodbye, font=("Verdana", 10), bg="indianred")
        goodbye_button.pack(side=tk.RIGHT, padx=(0, 40), pady=(0, 20))

    def download(self):
        global idClient
        global secretClient
        global userName
        global playlist
        idClient = self.name_entry.get()
        secretClient = self.name_clientSecret_text_entry.get()
        userName = self.name_clientName_text_entry.get()
        playlist = self.name_clientPlaylist_text_entry.get()
        self.after(5000, self.destroy)

    def say_goodbye(self):
        if msgbox.askyesno("Cerrar Ventana?", "Seguro desea salir?"):
            message = "Gracias por usar el programa, Saludos " + self.name_entry.get()
            self.label_text.set(message)
            self.after(1000, self.destroy)
        else:
            msgbox.showinfo("No cerrar", "Puede seguir usando el programa.")


def loadDataTxt():
    global txt_id
    global txt_user
    global txt_playlist
    global txt_secret

    with open("data.txt") as archivo:
        for linea in archivo:
            arg = linea.split("=")
            if arg[0] == "Client ID":
                txt_id = arg[1]
            elif arg[0] == "Client Secret":
                txt_secret = arg[1]
            elif arg[0] == "UserName":
                txt_user = arg[1]
            else:
                txt_playlist = arg[1]


if __name__ == "__main__":
    loadDataTxt()
    window = Window()
    window.mainloop()
    client_id = idClient
    client_secret = secretClient
    username = userName
    playlist_uri = playlist
    multicore_support = enable_multicore(autoenable=True, maxcores=None, buffercores=1)
    auth_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlist_name = write_playlist(username, playlist_uri)
    reference_file = "{}.txt".format(playlist_name)
    # Create the playlist folder
    if not os.path.exists(playlist_name):
        os.makedirs(playlist_name)
    os.rename(reference_file, playlist_name + "/" + reference_file)
    os.chdir(playlist_name)
    if multicore_support > 1:
        multicore_find_and_download_songs(reference_file, multicore_support)
    else:
        find_and_download_songs(reference_file)
    msgbox.showinfo("Fin del Proceso", "Se ha completado de descarga.")
    print("Operation complete.")
