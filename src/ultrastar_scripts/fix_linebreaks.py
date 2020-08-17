import argparse
import sys
import math

from ultrastar_scripts.libultrastar import (
    parseBPMLine,
    minute_fraction_between_beats
)

def _optimal_linebreak(firstBeat: int, secondBeat: int, bpm: float):
    fraction = minute_fraction_between_beats(firstBeat, secondBeat, bpm)
    pause = secondBeat - firstBeat
    if pause >= 2 and pause <= 8:
        # 2-8 beats
        return secondBeat - 2
    elif pause >= 9 and pause <= 12:
        # 9-12 beats
        return secondBeat - 3
    elif pause >= 13 and pause <= 16:
        # 13-16 beats
        return secondBeat - 4
    elif fraction > 0.066:
        # four seconds: two seconds after end
        return firstBeat + round(bpm/7.5)
    elif fraction > 0.033:
        # > two seconds: one second after end
        return firstBeat + math.floor(bpm/15)
    # ~ elif fraction > 0.016:
        # ~ # > one second: half a second after end
        # ~ return firstBeat + math.ceil(bpm/30)
    elif pause > 16:
        # more than 16 beats but < one second
        return firstBeat + 10
    # default: 1/3rd
    return firstBeat + math.ceil((secondBeat - firstBeat)/3)

def main():
    parser = argparse.ArgumentParser(description='Fix linebreaks in Ultrastar txt files')
    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='Input file (default: standard input)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='Output file (default: standard output)')
    args = parser.parse_args()
    output=args.output

    bpm = 0
    prevnoteline = ''
    linebreak = False
    for line in args.input.readlines():
        if line.startswith('#'):
            output.write(line)
            if line.startswith('#BPM:'):
                bpm = parseBPMLine(line)
        elif line.startswith('E') or line.startswith('P'):
            output.write(line)
        elif line.startswith('-'):
            linebreak = True
        else:
            if linebreak:
                # special handling if the last line was a linebreak
                prevparts = prevnoteline.split(' ', 3)
                prevend = int(prevparts[1]) + int(prevparts[2])
                start = int(line.split(' ')[1])
                output.write('- ' + str(_optimal_linebreak(prevend, start, bpm)) + '\n')
                linebreak = False
            # regular handling
            output.write(line)
            prevnoteline = line
