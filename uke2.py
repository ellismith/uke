"""This is the uke file - attept #2 """

from bs4 import BeautifulSoup as bs
import ipywidgets as widgets
from IPython.display import display, clear_output
import pandas as pd
import requests


#this stuff is global variables

notes = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

d = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

d_inv = {value: key for key, value in d.items()}

fifths = [
    d_inv[i % 12] for i in range(0, 12 * 7, 7)
]  

distances = (
    (0, "maj"),
    (2, "min"),
    (4, "min"),
    (5, "maj"),
    (6, "maj"),
    (9, "min"),
    (11, "dim"),
)


#classes are here

class Song: #inheritance is when attributes are still associated with the object
    chords_dict = None
    chord_counter = None
    original_key = None
    target_key = None
    response = None


def get_response(url):
    response = requests.get(url)
    return response


def get_all_chord_links(response):    
    soup = bs(response.text, features="lxml") #second argument is kwarg to specify how to parse the HTML
    all_chord_links = soup.findAll("a", {"class": "chord"})
    return all_chord_links
    

def transpose_note(old_note, offset):
    new_note = d_inv[(d[old_note] + offset) % 12]
    return new_note  # new_note only is a variable used within the function (scope is only within function)


def transpose_chord(chord, offset, target_key):
    note = chord[0]
    if len(chord) == 1:
        suffix = ""
    elif len(chord) > 1:
        suffix = chord[1:]  # 1: means every character 1 to the end
    new_note = transpose_note(note, offset)
    if fifths.index(target_key) < 6:
        new_note = flat_to_sharp(d, new_note)
    return new_note + suffix


def change_key(response, transpose_int, target_key):
    soup = bs(response.text, features="lxml")
    all_chord_links = soup.findAll("a", {"class": "chord"})
    for link in all_chord_links:
        new_chord = transpose_chord(link.text, transpose_int, target_key)
        link.string = new_chord
        link["title"] = new_chord + " "
    return soup


def get_all_chords(all_chord_links):
    all_chords = [link.text for link in all_chord_links]
    return all_chords


def flat_to_sharp(d, note):  # the d, uses the dictionary that I made
    if "b" in note:
        # how to go one position back in the list of all notes, to go b to #
        all_notes = list(d.keys())  # had to also make d.keys list
        i = all_notes.index(note) - 1  # position in the list
        note = all_notes[i]  # what is the note at position i in the list
    return note


def get_key_chords(key, distances):
    chords = []
    root = d[key]
    for i, mode in distances:
        note = d_inv[(root + i) % 12]
        if mode == "maj":
            suffix = ""  # The empty quotes ("") is empty string
        elif mode == "min":
            suffix = "m"
        elif mode == "dim":
            suffix = "dim"
        if fifths.index(key) < 6:
            note = flat_to_sharp(d, note)
        chords.append(note + suffix)  # append the string to the list "chords"
    return chords


def get_chords_dict():
    chords_dict = {key: get_key_chords(key, distances) for key in notes}
    return chords_dict


def get_chord_counter(all_chords):
    chord_counter = {}
    for chord in all_chords:
        if chord in chord_counter:
            chord_counter[chord] += 1
        else:
            chord_counter[chord] = 1
    return chord_counter



def get_chords_from_url(url):
    response = get_response(url)
    all_chord_links = get_all_chord_links(response)
    all_chords = get_all_chords(all_chord_links)
    return all_chords


def get_chords_dict_and_counter(url):
    all_chords = get_chords_from_url(url)
    chords_dict = get_chords_dict()
    chord_counter = get_chord_counter(all_chords)
    return chords_dict, chord_counter

    
def rank_keys(chords_dict, chord_counter):
    key_scores = {}
    for key, key_chords in chords_dict.items():
        key_scores[key] = 0
        for song_chord, num_times in chord_counter.items():
            if song_chord in key_chords:
                key_scores[key] += num_times
    return key_scores


