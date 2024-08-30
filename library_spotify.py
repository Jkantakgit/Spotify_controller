##
# @file library_spotify.py
#
# @brief library for main program with functions for mqtt connetions and spotify API calls
#
#
# @section author_doxygen_example Author(s)
# - Created by Petr Holánek on 30.8.2024.
# - Modified by Petr Holánek on 30.8.2024.
#

#imports
from tkinter.constants import E, HORIZONTAL, W
import spotipy
import threading
import time
from PIL import Image, ImageTk
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import requests
import tkinter as tk
from functools import partial
from tkinter.ttk import Progressbar, Style
import pyautogui
import ctypes
from paho.mqtt import client as cl
import random


#mqtt configurations
broker = "10.180.0.9"
port = 1883
topic = [("zigbee2mqtt/Dvere Petr", 0), ("zigbee2mqtt/tlacitko", 0)]
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = ""
password = ""

#function for getting acess token for spotify API
def get_token(id, secret, uri, scope):
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=id, client_secret=secret, redirect_uri=uri, scope=scope
        )
    )
    return sp

#Helper function to keep track of saved tracks
def make_lists_of_tracks(sp, error):
    error = None
    f = open("Ids.txt", "w")
    f.close()
    f = open("Ids.txt", "a")
    try:
        off = 0
        while True:
            a = sp.current_user_saved_tracks(limit=2, offset=off)
            off += 2
            b = a.get("items")[0].get("track").get("id")
            c = a.get("items")[1].get("track").get("id")
            f.write(b + "\n")
            f.write(c + "\n")
    except Exception as s:
        if type(s) is IndexError:
            pass
        else:
            error = True
    f.close()
    if error:
        f = open("Ids.txt", "w")
        f.write("Error in track list, 001")
        f.close()

#Spotify API callback to stop current track playback
def callback_stop(Stop, window, img_stop):
    Stop.configure(image=img_stop)
    Stop.image = img_stop
    window.update_idletasks()

#Spotify API callback to resume current track playback
def callback_play(Stop, window, img_play):
    Stop.configure(image=img_play)
    Stop.image = img_play
    window.update_idletasks()

#helper function to convert miliseconds to minutes and seconds in a minutes:seconds format
def ms_to_min(progress):
    b = (progress / 1000) % 60
    b = int(b)
    c = (progress / (1000 * 60)) % 60
    c = int(c)
    progress_min = "%d:%d" % (c, b)
    return progress_min

#function to get current playing track cover image
def get_img(item):
    album = item.get("album")
    images = album.get("images")
    image = images[2]
    imag = image.get("url")
    with open("./resources/alb.png", "wb") as fil:
        response = requests.get(imag)
        fil.write(response.content)

#helper function for author name lenght, if the name is too long it crops it
def check_author_lenghts(item):
    artist = ""
    artist_list = item.get("artists")
    while True:
        string = ""
        for artists in artist_list:
            artists = artists["name"]
            string += artists
        if len(string) > 33:
            artist_list.pop()
        else:
            break
    b = 0
    for artists in artist_list:
        if (b + 1) < len(artist_list):
            artist += artists.get("name") + ", "
        else:
            artist += artists.get("name")
        b += 1
    return artist

#helper function for changing cover picture
def change_alb_pic(Panel, window):
    alb_img = ImageTk.PhotoImage(Image.open("./resources/alb.png"))
    Panel.config(image=alb_img)
    Panel.image = alb_img
    window.update_idletasks()

#calculates progress bar progress based on current time and maximum time
def progress_values(a, b):
    c = a / b
    t = c * 100
    return t

#function that gets all track info from spotify API
def track_info(
    sp,
    Stop,
    window,
    Panel,
    img_play,
    img_stop,
    progress,
    trackname,
    current_authors,
    maxs_time,
    prog,
    error,
):
    a = 1
    id_song = "Not set"
    is_playing_char = False
    while True:
        while check_internet() == False:
            time.sleep(1)
        sp = initilaize_tokens()
        time.sleep(0.1)
        try:
            current_track_info = sp.current_user_playing_track()
            if current_track_info:
                is_playing_char = current_track_info["is_playing"]
            if is_playing_char:
                item = current_track_info.get("item")
                max_time = item.get("duration_ms")
                progress_ms = current_track_info.get("progress_ms")
                progress_char = ms_to_min(progress_ms)
                progress.set(progress_char)
                if item:
                    if id_song != item.get("name"):
                        get_img(item=item)
                        change_alb_pic(Panel, window)
                        track_name = item.get("name")
                        if len(track_name) > 33:
                            track_name = track_name[:33] + "..."
                        trackname.set(track_name)
                        authors = check_author_lenghts(item)
                        current_authors.set(authors)
                        maxim_time = ms_to_min(max_time)
                        maxs_time.set(maxim_time)
                        t = progress_values(progress_ms, max_time)
                        prog["value"] = t
                        window.update_idletasks()
                    if a == 1:
                        change_alb_pic(Panel, window)
                        a = 0
                        id_song = item.get("id")
                        callback_stop(Stop, window, img_stop)
                else:
                    continue
            else:
                if a == 0:
                    callback_play(Stop, window, img_play)
                    img2 = Image.new("1", (64, 64))
                    img2.save("./resources/alb.png")
                    change_alb_pic(Panel, window)
                a = 1
        except Exception as s:
            error.set("Error in track thread, 002(%s)" % s)

#Creates thread for making list of saved songs
def id(sp, error):
    t = threading.Thread(target=make_lists_of_tracks, args=[sp, error], daemon=True)
    t.setName("ID")
    return t

#function that reads saved songs from file and splits it into array
def read_ids():
    f = open("Ids.txt", "r")
    ids = f.read()
    ids = ids.splitlines()
    return ids

#initializes variables from file
def initialize_variables():
    f = open("variables", "r")
    string = f.read()
    string = string.splitlines()
    scope = string[0]
    Id = string[1]
    Secret = string[2]
    Url = string[3]
    return scope, Id, Secret, Url

#Creates blank picture when no song is playing
def make_black_pic():
    img2 = Image.new("1", (64, 64))
    img2.save("./resources/alb.png")

#initializes elements for window with functions and styles
def initialize_windowns_and_buttons(
    alb_img,
    stop_img,
    sp,
    spotify_window,
    track_name,
    current_author,
    progress,
    maxs_time,
    next_img,
    prev_img,
    like_non,
    mode,
    window,
    var_time,
):
    style = Style()
    style.theme_use("default")
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="black",
        lightcolor="black",
        bordercolor="black",
        background="grey",
        thickness=5,
    )
    Panel = tk.Label(image=alb_img, borderwidth=0)
    Stop = tk.Button(
        image=stop_img,
        bg="black",
        bd=0,
        command=partial(stop_play, sp),
        height=17,
        activebackground="black",
    )
    prog = Progressbar(
        window,
        style="TProgressbar",
        orient=HORIZONTAL,
        length=400,
        mode="determinate",
    )
    Track = tk.Label(
        textvariable=track_name, foreground="white", background="black", width=30
    )
    Author = tk.Label(
        textvariable=current_author, foreground="white", background="black", width=30
    )
    Time = tk.Label(
        textvariable=progress, foreground="white", background="black", width=15
    )
    max_times = tk.Label(
        textvariable=maxs_time, foreground="white", background="black", width=15
    )
    next_butt = tk.Button(
        image=next_img,
        bg="black",
        bd=0,
        command=partial(next_track, sp),
        activebackground="black",
    )
    prev_butt = tk.Button(
        image=prev_img,
        bg="black",
        bd=0,
        command=partial(previous_track, sp),
        activebackground="black",
    )
    like_butt = tk.Button(
        image=like_non,
        activebackground="black",
        command=partial(like_trk, sp),
        bg="black",
        bd=0,
    )
    nothing_mode = tk.Button(
        spotify_window, text="Set nothing", command=partial(set_mothing, mode)
    )
    stop_mode = tk.Button(
        spotify_window, text="Set stop", command=partial(set_stop, mode)
    )
    stop_lock_mode = tk.Button(
        spotify_window,
        text="Set stop and lock",
        command=partial(set_lock_and_stop, mode),
    )
    mode_label = tk.Label(
        spotify_window, textvariable=mode, background="black", foreground="white"
    )
    time_label = tk.Label(
        spotify_window, textvariable=var_time, background="black", foreground="white"
    )
    return (
        Panel,
        Stop,
        prog,
        Track,
        Author,
        Time,
        max_times,
        next_butt,
        prev_butt,
        like_butt,
        nothing_mode,
        stop_mode,
        stop_lock_mode,
        mode_label,
        time_label,
    )

#Function thast checks playback and resumes or stops song based on that information
def stop_play(sp):
    current_track_info = sp.current_user_playing_track()
    try:
        state = current_track_info.get("is_playing")
    except:
        state = False
    if state:
        sp.pause_playback()
    else:
        sp.start_playback()

#Initializes pictures from assets
def initialize_pictures():
    like_non = ImageTk.PhotoImage(Image.open("./resources/like_non.png"))
    next_img = tk.PhotoImage(file="./resources/Next_butt.png")
    next_img = next_img.subsample(2, 2)
    play_img = ImageTk.PhotoImage(Image.open("./resources/Play_butt.png"))
    prev_img = tk.PhotoImage(file="./resources/Prev_butt.png")
    prev_img = prev_img.subsample(2, 2)
    stop_img = ImageTk.PhotoImage(Image.open("./resources/Stop_butt.png"))
    alb_img = ImageTk.PhotoImage(Image.open("./resources/alb.png"))
    return like_non, next_img, play_img, prev_img, stop_img, alb_img

#initializes string variables for names and timestamps
def initialize_StringVar():
    current_authors = tk.StringVar()
    trackname = tk.StringVar()
    progress = tk.StringVar()
    maxs_time = tk.StringVar()
    var_time = tk.StringVar()
    mode = tk.StringVar()
    error = tk.StringVar()
    mode.set("stop")
    return current_authors, trackname, progress, maxs_time, var_time, mode, error

#initializes layout for window with elements
def initialize_window(
    Panel,
    Track,
    Author,
    Stop,
    like_butt,
    Time,
    prog,
    prev_butt,
    next_butt,
    max_times,
    window,
    nothing_mode,
    stop_mode,
    stop_lock_mode,
    mode_label,
    time_label,
):
    mode_label.grid(row=0, column=0, columnspan=3)
    nothing_mode.grid(row=1, column=0)
    stop_mode.grid(row=1, column=1)
    stop_lock_mode.grid(row=1, column=2)
    Panel.grid(row=0, column=0, columnspan=2, rowspan=2)
    Track.grid(row=0, column=2, sticky=W + E)
    Author.grid(row=1, column=2, sticky=W + E)
    Stop.grid(row=0, column=9)
    like_butt.grid(row=0, column=3)
    Time.grid(row=1, column=3)
    prog.grid(row=1, column=4, columnspan=10, ipady=0.001)
    prev_butt.grid(row=0, column=8)
    next_butt.grid(row=0, column=10)
    max_times.grid(row=1, column=14)
    time_label.grid(row=3, columnspan=3)
    window.grid_columnconfigure(0, weight=1)
    window.bind("<Return>", callback_stop)

#API call for skipping song
def next_track(sp):
    sp.next_track()

#API call for gooing to previous song or begining of current song
def previous_track(sp):
    sp.previous_track()

#Adds or removes song from saved tracks
def like_trk(sp):
    ids = read_ids()
    track = [sp.current_user_playing_track().get("item").get("uri")]
    id = sp.current_user_playing_track().get("item").get("id")
    if id in ids:
        sp.current_user_saved_tracks_delete(track)
        ids.remove(id)
    elif id not in ids:
        sp.current_user_saved_tracks_add(track)
        ids.append(id)
    f = open("Ids.txt", "w")
    for i in ids:
        f.write(i + "\n")
    f.close()

#Changes heart element based on if the song is saved or not
def change_like_pic(sp, window, like_butt):
    like_no = tk.PhotoImage(file="./resources/like_non.png")
    like_non = like_no.subsample(2, 2)
    lik = tk.PhotoImage(file="./resources/like.png")
    like = lik.subsample(2, 2)
    while True:
        try:
            id = sp.current_user_playing_track().get("item").get("id")
            playback = True
        except:
            playback = False
        if playback:
            ids = read_ids()
            if id in ids:
                like_butt.config(image=like)
                like_butt.image = like
            else:
                like_butt.config(image=like_non)
                like_butt.image = like_non
            window.update_idletasks()
        time.sleep(0.3)

#thread for checking saved songs in the background
def like_pic_change(sp, window, like_butt):
    t = threading.Thread(
        target=change_like_pic, args=[sp, window, like_butt], daemon=True
    )
    t.setName("Like_pic")
    return t

#initializes mqtt client and subscribes to topics
def mqtt(mode, var_time):
    client = connect()
    subscribe(client, var_time, mode)
    client.loop_forever()

#connects to mqtt server
def connect():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code {code}".format(rc))

    client = cl.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

#subscribes to mqtt topic
def subscribe(client, var_time, mode):
    def on_message(client, userdata, msg):
        print(msg.payload.decode())
        if (
            """"contact":false""" in msg.payload.decode()
            or '''"click":"double"''' in msg.payload.decode()
        ):
            now = datetime.now()
            čas = now.strftime("%H:%M:%S")
            var_time.set(čas)
            mod = mode.get()
            if mod == "nothing":
                pass
            elif mod == "stop":
                print("Stopped")
                pyautogui.press("stop")
            elif mod == "lock_and_stop":
                pyautogui.press("stop")
                ctypes.windll.user32.LockWorkStation()

    client.subscribe(topic)
    client.on_message = on_message

#helper function for notifying thread that makes list of saved song when to run again
def id_recheck_thread(sp, error):
    end = None
    start = time.time()
    while True:
        end = time.time()
        diff = end - start
        if diff > 900:
            make_lists_of_tracks(sp, error)
            start = time.time()
        time.sleep(1)

#thread that rechecks saved songs
def recheck(sp, error):
    t = threading.Thread(target=id_recheck_thread, daemon=True, args=[sp, error])
    t.setName("Ids_recheck")
    return t

#sets mode of door sensor to stopping mode (stops playback when doors open)
def set_stop(mode):
    mode.set("stop")

#sets mode of door sensor to nothing mode (nothing happens when doors open)
def set_mothing(mode):
    mode.set("nothing")

#sets mode of door sensor to lock and stop mode (stops playback and lock computer when doors open)
def set_lock_and_stop(mode):
    mode.set("lock_and_stop")

#error tracking function
def error_func(error):
    while True:
        err = error.get()
        if (
            err
            and err[0:111]
            == "Error in track thread, 002(HTTPSConnectionPool(host='api.spotify.com', port=443): Max retries exceeded with url"
        ):
            pass
        elif err:
            window = tk.Toplevel()
            exit_button = tk.Button(text="Exit", command=window.destroy, master=window)
            Ok_button = tk.Button(text="Ok", command=window.destroy, master=window)
            label = tk.Label(text=err, master=window)
            label.pack()
            exit_button.pack()
            Ok_button.pack()
            error.set("")
        time.sleep(120)

#thread for checking if error occured
def Error_thread(error):
    t = threading.Thread(target=error_func, args=[error])
    t.setName("Error_thread")
    return t

#makes pool of threads to start
def make_list_of_threads(
    sp,
    window,
    like_butt,
    Stop,
    Panel,
    play_img,
    stop_img,
    progress,
    trackname,
    current_authors,
    maxs_time,
    prog,
    error,
    mode,
    var_time,
):
    threads = []
    threads.append(id(sp, error))
    threads.append(like_pic_change(sp, window, like_butt))
    threads.append(
        get_main_thread(
            sp,
            Stop,
            window,
            Panel,
            play_img,
            stop_img,
            progress,
            trackname,
            current_authors,
            maxs_time,
            prog,
            error,
        )
    )
    threads.append(recheck(sp, error))
    threads.append(threading.Thread(target=mqtt, args=[mode, var_time]))
    # threads.append(Error_thread(error))
    return threads

#starts whole pool of threads
def start_threads(
    sp,
    window,
    like_butt,
    Stop,
    Panel,
    play_img,
    stop_img,
    progress,
    trackname,
    current_authors,
    maxs_time,
    prog,
    error,
    mode,
    var_time,
):
    threads = make_list_of_threads(
        sp,
        window,
        like_butt,
        Stop,
        Panel,
        play_img,
        stop_img,
        progress,
        trackname,
        current_authors,
        maxs_time,
        prog,
        error,
        mode,
        var_time,
    )
    for i in threads:
        i.start()

#makes main thread
def get_main_thread(
    sp,
    Stop,
    window,
    Panel,
    play_img,
    stop_img,
    progress,
    trackname,
    current_authors,
    maxs_time,
    prog,
    error,
):
    t = threading.Thread(
        target=track_info,
        args=[
            sp,
            Stop,
            window,
            Panel,
            play_img,
            stop_img,
            progress,
            trackname,
            current_authors,
            maxs_time,
            prog,
            error,
        ],
        daemon=True,
    )
    t.setName("Mainthread")
    return t

# runs all threads including main thread
def run_all():
    while check_internet() == False:
        time.sleep(1)
    sp = initilaize_tokens()
    make_black_pic()
    window, spotify_window = initialize_tkinter()
    like_non, next_img, play_img, prev_img, stop_img, alb_img = initialize_pictures()
    (
        current_authors,
        trackname,
        progress,
        maxs_time,
        var_time,
        mode,
        error,
    ) = initialize_StringVar()
    (
        Panel,
        Stop,
        prog,
        Track,
        Author,
        Time,
        max_times,
        next_butt,
        prev_butt,
        like_butt,
        nothing_mode,
        stop_mode,
        stop_lock_mode,
        mode_label,
        time_label,
    ) = initialize_windowns_and_buttons(
        alb_img,
        stop_img,
        sp,
        spotify_window,
        trackname,
        current_authors,
        progress,
        maxs_time,
        next_img,
        prev_img,
        like_non,
        mode,
        window,
        var_time,
    )
    initialize_window(
        Panel,
        Track,
        Author,
        Stop,
        like_butt,
        Time,
        prog,
        prev_butt,
        next_butt,
        max_times,
        window,
        nothing_mode,
        stop_mode,
        stop_lock_mode,
        mode_label,
        time_label,
    )
    start_threads(
        sp,
        window,
        like_butt,
        Stop,
        Panel,
        play_img,
        stop_img,
        progress,
        trackname,
        current_authors,
        maxs_time,
        prog,
        error,
        mode,
        var_time,
    )
    spotify_window.grid()
    window.mainloop()

#initializes tkinter windows
def initialize_tkinter():
    window = tk.Tk()
    window.configure(bg="black")
    window.resizable(False, False)
    window.title("Spotify")
    window.geometry("+-1090+1600")
    spotify_window = tk.Toplevel()
    spotify_window.resizable(False, False)
    spotify_window.configure(bg="black")
    spotify_window.title("Senzor dveře")
    spotify_window.geometry("+-2895+1600")
    return window, spotify_window

#initializes tokens
def initilaize_tokens():
    (
        scope,
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_CLIENT_REDIRECT_URI,
    ) = initialize_variables()
    sp = get_token(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_CLIENT_REDIRECT_URI, scope
    )
    return sp

#checks for internet connection
def check_internet():
    url = "http://www.kite.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        print("No internet")
        return False
