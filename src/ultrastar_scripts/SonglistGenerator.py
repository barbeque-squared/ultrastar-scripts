import sys
import csv
from SongType import SongType
from pathlib import Path

class SonglistGenerator:
    __songlist = {}
    
    def __init__(self, paths: [str]):
        self.__paths = paths
    
    def generate(self):
        for path in self.__paths:
            for p in Path(path).glob('**/*.txt'):
                song = self._loadSong(p)
                if song:
                    identifier = song.identifier()
                    if identifier in self.__songlist:
                        self.__songlist[identifier].addVariant(song.songtype)
                    else:
                        self.__songlist[identifier] = self._SonglistEntry(song.artist, song.title, song.songtype)
                else:
                    sys.stderr.write(str(p) + ' does not look like a song file, skipping\n')

    def getSonglist(self):
        return __songlist

    def writeCsv(self, output):
        writer = csv.writer(output)
        writer.writerow([
            'Artist',
            'Title',
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
                int(SongType.LOSSY in entry.variants),
                int(SongType.INSTRUMENTAL in entry.variants),
                int(SongType.DUET in entry.variants),
                int(SongType.INSTRUMENTAL_DUET in entry.variants),
                int(SongType.LOSSLESS in entry.variants),
                int(SongType.LOSSLESS_INSTRUMENTAL in entry.variants),
                int(SongType.LOSSLESS_DUET in entry.variants),
                int(SongType.LOSSLESS_INSTRUMENTAL_DUET in entry.variants)
            ])

    def _loadSong(self, path: str):
        artist = None
        title = None
        with open(path) as reader:
            try:
                for line in reader:
                    if line.startswith('#ARTIST:'):
                        artist = line.strip().replace('#ARTIST:', '', 1)
                    elif line.startswith('#TITLE:'):
                        title = line.strip().replace('#TITLE:', '', 1)
                    if artist is not None and title is not None:
                        return self._Song(artist, title)
            except UnicodeDecodeError as ude:
                raise Exception('error while loading ' + str(path)) from ude

    class _Song:
        def __init__(self, artist: str, title: str):
            songtype = SongType.LOSSY
            self.artist = artist
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
            return ' - '.join([self.artist, self.title])

    class _SonglistEntry:
        def __init__(self, artist: str, title: str, songtype: SongType):
            self.artist = artist
            self.title = title
            self.variants = [songtype]

        def addVariant(self, songtype: SongType):
            self.variants.append(songtype)