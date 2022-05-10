# BPM
def parseBPMLine(line: str) -> float:
    return parseBPM(line.split(':')[1])

def parseBPM(bpm: str) -> float:
    return float(bpm.strip().replace(',', '.', 1))

def minute_fraction_between_beats(firstBeat: int, secondBeat: int, bpm: float) -> float:
    if bpm <= 0:
        raise ValueError('BPM must be positive')
    elif secondBeat < firstBeat:
        raise ValueError('secondBeat (' + str(secondBeat) + ') must be equal to or greater than firstBeat (' + str(firstBeat) + ')')
    return (secondBeat - firstBeat) / (bpm*4)

# output
def print_error(*args, **kwargs):
    from sys import stderr
    if 'file' in kwargs:
        del kwargs['file']
    print(*args, file=stderr, **kwargs)
