def parseFloatLine(line: str) -> float:
    return parseFloat(line.split(':', 1)[1])

def parseFloat(val: str) -> float:
    return float(val.strip().replace(',', '.', 1))

def parseIntLine(line: str) -> int:
    return parseInt(line.split(':', 1)[1])

def parseInt(val: str) -> int:
    return int(val)

def parseTextLine(line: str) -> str:
    val = line.split(':', 1)[1].strip()
    if len(val) == 0:
        return None
    return val

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
