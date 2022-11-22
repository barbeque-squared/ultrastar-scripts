import sys
import csv
import json
from pathlib import Path
from enum import IntFlag
import yaml
from itertools import chain

class SongType(IntFlag):
    # base values
    LOSSY = 0
    LOSSLESS = 1
    INSTRUMENTAL = 2
    DUET = 4
    # combinations
    INSTRUMENTAL_DUET = INSTRUMENTAL | DUET
    LOSSLESS_INSTRUMENTAL = LOSSLESS | INSTRUMENTAL
    LOSSLESS_DUET = LOSSLESS | DUET
    LOSSLESS_INSTRUMENTAL_DUET = LOSSLESS | INSTRUMENTAL | DUET


class SonglistEntry:
    def __init__(self, artist: str, title: str, language: str, songtype: SongType, dmx: int):
        self.artist = artist
        self.title = title
        self.language = language
        self.variants = [songtype]
        self.dmx = dmx

    def __iter__(self):
        yield 'artist', self.artist
        yield 'title', self.title
        yield 'language', self.language
        yield 'variants', self.variants
        yield 'dmx', self.dmx

    def addVariant(self, songtype: SongType):
        self.variants.append(songtype)


class SonglistGenerator:
    __songlist = {}
    
    def __init__(self, paths: [str], dmxpaths: [str] = []):
        self.__paths = paths
        self.__dmxpaths = dmxpaths
        self._dmxconfig = self._loadDmxConfig()
    
    def generate(self):
        for path in self.__paths:
            for p in Path(path).glob('**/*.txt'):
                song = self._loadSong(p)
                if song:
                    identifier = song.identifier()
                    if identifier in self.__songlist:
                        if self.__songlist[identifier].language != song.language:
                            sys.stderr.write(str(p) + ' uses different language\n')
                        self.__songlist[identifier].addVariant(song.songtype)
                    else:
                        self.__songlist[identifier] = SonglistEntry(song.artist, song.title, song.language, song.songtype, song.dmx)
                else:
                    sys.stderr.write(str(p) + ' does not look like a song file, skipping\n')

    def getSonglist(self):
        return [entry for identifier, entry in sorted(self.__songlist.items())]

    def writeCsv(self, output):
        writer = csv.writer(output)
        writer.writerow([
            'Artist',
            'Title',
            'Language',
            'Lossy',
            'Lossy Instrumental',
            'Lossy Duet',
            'Lossy Duet Instrumental',
            'Lossless',
            'Lossless Instrumental',
            'Lossless Duet',
            'Lossless Duet Instrumental'
        ])
        for identifier, entry in sorted(self.__songlist.items()):
            writer.writerow([
                entry.artist,
                entry.title,
                entry.language,
                int(SongType.LOSSY in entry.variants),
                int(SongType.INSTRUMENTAL in entry.variants),
                int(SongType.DUET in entry.variants),
                int(SongType.INSTRUMENTAL_DUET in entry.variants),
                int(SongType.LOSSLESS in entry.variants),
                int(SongType.LOSSLESS_INSTRUMENTAL in entry.variants),
                int(SongType.LOSSLESS_DUET in entry.variants),
                int(SongType.LOSSLESS_INSTRUMENTAL_DUET in entry.variants)
            ])

    def writeJson(self, output):
        with open(output, 'w') as outfile:
            json.dump({'songlist': list(map(dict, self.getSonglist()))}, outfile, indent=4)

    ### DMX/YAML FUNCTIONS START ###
    def _loadDmxConfig(self):
        res = []
        for path in self.__dmxpaths:
            dmxs = list(map(lambda p: self._loadDmxFile(p), Path(path).rglob('*.yml')))
            res += list(chain.from_iterable(dmxs))
        return res

    def _loadDmxFile(self, path):
        with open(path, 'r') as p:
            res = []
            for c in yaml.safe_load_all(p):
                dmxcount = 1 + len(c.get('instructions', []))
                res.append({'artist': c['artist'], 'title': c['title'], 'same-as': c.get('same-as'), 'dmx': dmxcount, 'path': p.name})
            return res

    # will return the config obj for the best match, or None if nothing matches
    def _bestDmxConfigMatch(self, artist: str, title: str):
        l_artist = artist.lower()
        l_title = title.lower()
        candidates = list(filter(
            lambda o: l_artist.startswith(o['artist'].lower()) and l_title.startswith(o['title'].lower()),
            self._dmxconfig
        ))
        if len(candidates) < 1:
            return None
        song = max(candidates, key=lambda c: len(c['artist']+c['title']))
        if song['same-as'] is not None:
            artist = song['same-as'].get('artist', song['artist'])
            title = song['same-as'].get('title', song['title'])
            # WARNING: there is no infinite recursion safeguarding
            song = self._bestDmxConfigMatch(artist, title)
        return song
    
    def _dmxCount(self, artist: str, title: str):
        match = self._bestDmxConfigMatch(artist, title)
        if match:
            return match['dmx']
        return 0
    ### DMX/YAML FUNCTIONS END ###

    def _loadSong(self, path: str):
        artist = None
        title = None
        language = None
        with open(path) as reader:
            try:
                for line in reader:
                    # remove BOM
                    if line.startswith('\ufeff'):
                        line = line[1:]
                    if line.startswith('#ARTIST:'):
                        artist = line.strip().replace('#ARTIST:', '', 1)
                    elif line.startswith('#TITLE:'):
                        title = line.strip().replace('#TITLE:', '', 1)
                    elif line.startswith('#LANGUAGE:'):
                        language = line.strip().replace('#LANGUAGE:', '', 1)
                    if artist is not None and title is not None and language is not None:
                        dmx = self._dmxCount(artist, title)
                        return self._Song(artist, title, language, dmx)
                    elif not line.startswith('#') and (artist is not None or title is not None or language is not None):
                        if artist is None:
                            raise Exception(str(path) + ' does not set #ARTIST')
                        elif title is None:
                            raise Exception(str(path) + ' does not set #TITLE')
                        elif language is None:
                            raise Exception(str(path) + ' does not set #LANGUAGE')
            except UnicodeDecodeError as ude:
                raise Exception('error while loading ' + str(path)) from ude

    class _Song:
        def __init__(self, artist: str, title: str, language: str, dmx: int):
            songtype = SongType.LOSSY
            self.artist = artist
            self.language = language
            self.dmx = dmx
            # parse title
            types = {
                '(Lossless)': SongType.LOSSLESS,
                '(Instrumental)': SongType.INSTRUMENTAL,
                '(Duet)': SongType.DUET
            }
            for k, v in types.items():
                if k in title:
                    songtype |= v
                    title = title.replace(k, '')
            self.songtype = songtype
            # removes duplicate spaces
            self.title = ' '.join(title.split())

        def identifier(self):
            return ' - '.join([self.artist, self.title]).casefold()
