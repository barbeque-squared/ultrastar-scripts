import argparse
import sys
import math
from pathlib import Path

from ultrastar_scripts.libultrastar import (
    parseBPMLine,
    minute_fraction_between_beats,
    print_error
)

def _fileerror(filename: str, message: str):
    print_error('{}: {}'.format(filename, message))

def _lineerror(filename: str, linenumber: int, songlinenumber: int, message: str):
    print_error('{} line {} (s{}): {}'.format(filename, linenumber, songlinenumber, message))

def _noteerror(filename: str, linenumber: int, songlinenumber: int, songlinenotenumber: int, message: str):
    print_error('{} line {} (s{}n{}): {}'.format(filename, linenumber, songlinenumber, songlinenotenumber, message))

def _error(filename: str, linenumber: int, message: str):
    print_error('{} line {}: {}'.format(filename, linenumber, message))

def main():
    parser = argparse.ArgumentParser(description='Check Ultrastar txt files')
    parser.add_argument('path', nargs='?', type=str, default='.', help='Path to look for txt files (default: .)')
    args = parser.parse_args()
    path=args.path

    for p in sorted(Path(path).glob('**/*.txt')):
        with open(p) as reader:
            end = False
            bpm = 0
            two_seconds = 0
            prevnoteline = None
            prevlinebreak = None
            songlinenum = 1
            songlinenotenum = 0
            # golden note computations: ideally, 1/17 of all notes are golden (this equals 8000 normal points + 1000 golden points)
            totalBeats = 0
            goldenBeats = 0
            for i, line in enumerate(reader):
                if end:
                    _error(p, i, 'extra lines after end')
                elif line.startswith('#BPM'):
                    bpm = parseBPMLine(line)
                elif line.startswith('P'):
                    prevnoteline = None
                    prevlinebreak = None
                elif line.startswith('-'):
                    # linebreak
                    if prevlinebreak:
                        _error(p, i, 'multiple linebreaks')
                    if not prevnoteline:
                        _error(p, i, 'linebreak without preceding note')
                    else:
                        prevparts = prevnoteline.split(' ')
                        prevend = int(prevparts[1]) + int(prevparts[2])
                        linebreak = int(line.split(' ')[1])
                        if linebreak < prevend:
                            _error(p, i, 'linebreak too early')
                        elif linebreak - 3 < prevend:
                            _lineerror(p, i, songlinenum, 'linebreak less than 3 beats after note end')
                    prevlinebreak = line
                    songlinenum += 1
                    songlinenotenum = 0
                elif line.startswith('E'):
                    end = True
                elif not line.startswith('#'):
                    songlinenotenum += 1
                    # note
                    parts = line.split(' ', 4)
                    thistype = parts[0]
                    thislength = int(parts[2])
                    if thistype != 'F':
                        totalBeats += thislength
                        if thistype == '*':
                            goldenBeats += thislength

                    if prevnoteline:
                        prevparts = prevnoteline.split(' ', 4)
                        prevlength = int(prevparts[2])
                        prevend = int(prevparts[1]) + prevlength
                        start = int(parts[1])
                        if start < prevend:
                            _error(p, i, 'note starts too early')
                        else:
                            text = parts[4]
                            prevtype = prevparts[0]
                            # ignore if either of the notes is freestyle, or if the note length <= the gap
                            if prevtype != 'F' and thistype != 'F' and start - prevend < thislength:
                                if text.startswith(' '):
                                    # new word in sentence
                                    # ignore if previous note is also short
                                    if start - 3 < prevend and (thislength > 3 or prevlength > thislength):
                                        _noteerror(p, i, songlinenum, songlinenotenum, 'new word "'+text.strip()+'" starts less than 3 beats after previous word')
                                else:
                                    # next syllable of word
                                    # ignore if previous note is also short
                                    if start - 2 < prevend and (thislength > 2 or prevlength > thislength):
                                        _noteerror(p, i, songlinenum, songlinenotenum, 'syllable "'+text.strip()+'" starts less than 2 beats after previous syllable')

                        if prevlinebreak:
                            # do some extra linebreak-related checks
                            linebreak = int(prevlinebreak.split(' ')[1])
                            if start < linebreak:
                                _error(p, i, 'note starts too early')
                            elif start - 1 < linebreak:
                                _error(p, i, 'note starts less than 1 beat after linebreak')
                            # check if the linebreak is at a sensible place
                            # shared code with fix_linebreaks is deliberately duplicated for performance
                            fraction = minute_fraction_between_beats(prevend, start, bpm)
                            pause = start - prevend
                            if pause >= 2 and pause <= 8:
                                # 2-8 beats
                                optimalLinebreak = start - 2
                                if linebreak != optimalLinebreak:
                                    _error(p, i, 'pause is 2-8 beats, so linebreak 2 beats before (beat {})'.format(optimalLinebreak))
                            if pause >= 9 and pause <= 12:
                                # 9-12 beats
                                optimalLinebreak = start - 3
                                if linebreak != optimalLinebreak:
                                    _error(p, i, 'pause is 9-12 beats, so linebreak 3 beats before (beat {})'.format(optimalLinebreak))
                            elif pause >= 13 and pause <= 16:
                                # 13-16 beats
                                optimalLinebreak = start - 4
                                if linebreak != optimalLinebreak:
                                    _error(p, i, 'pause is 13-16 beats, so linebreak 4 beats before (beat {})'.format(optimalLinebreak))
                            elif fraction > 0.066:
                                # four seconds
                                optimalLinebreak = prevend + round(bpm/7.5)
                                if linebreak != optimalLinebreak:
                                    _error(p, i, 'pause is more than 4s, so linebreak after 2s (beat {})'.format(optimalLinebreak))
                            elif fraction > 0.033:
                                # > two seconds
                                optimalLinebreak = prevend + math.floor(bpm/15)
                                if linebreak != optimalLinebreak:
                                    _error(p, i, 'pause is more than 2s, so linebreak after 1s (beat {})'.format(optimalLinebreak))
                            # ~ elif fraction > 0.016:
                                # ~ # > one second
                                # ~ optimalLinebreak = prevend + math.ceil(bpm/30)
                                # ~ if linebreak != optimalLinebreak:
                                    # ~ _error(p, i, 'pause is more than 1s, so linebreak after 0.5s (beat {})'.format(optimalLinebreak))
                            elif pause > 16:
                                optimalLinebreak = prevend + 10
                                if linebreak != optimalLinebreak:
                                    _error(p, i, 'pause is more than 16 beats but less than 1s, so linebreak after 10 beats (beat {})'.format(optimalLinebreak))

                            prevlinebreak = None

                    prevnoteline = line
            # golden note computations
            idealGoldenBeats = round(totalBeats / 17)
            if goldenBeats != idealGoldenBeats:
                _fileerror(p, 'ideal golden beats = ' + str(idealGoldenBeats) + ' (current = ' + str(goldenBeats) + ')')
