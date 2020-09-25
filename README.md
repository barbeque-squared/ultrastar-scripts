# Ultrastar-scripts
A collection of (Python) scripts that might make editing and creating
songfiles for Ultrastar easier.

## Short guide
### check
Scans txt files in directories for most common errors. Most of what it
checks for is inspired by Yass and requirements for My Little Karaoke

### fix-linebreaks
Puts linebreaks in sensible places

### fix-whitespace
Sometimes you get a file where there is a space at the end of certain
notes. This moves those spaces in front of the next note instead.

### multiply-bpm
Sometimes you get a low-bpm file and you want to triple or quintuple the BPM
instead of being limited to doubling. Also accepts float values.

### split-lyrics
More or less smartly splits up a note that contains _ or + signs into
multiple separate notes. The result will always:

* have the same start beat as the original note
* have the same end beat as the original note
* as many notes as are necessary are each separated by 1 beat
* all except the last note are of the same length

### songlist-csv
Given one or more directories, create a csv of all the different versions.
Currently detects lossless, instrumental, duets and combinations thereof.
You can also `import SonglistGenerator` in your own scripts:

```
import SonglistGenerator

sg = SonglistGenerator(['/path/1', '/path/2'])
sg.generate()
songs = sg.getSonglist()
```

## The general workflow
These scripts support very much a divide-and-conquer workflow when it comes
to creating new songs, in the sense that generally, we first time entire
sentences, then separate words, and finally syllables. Less time is spent
moving whole groups of syllables around.

How this roughly works:

* Tap entire sentences in Ultrastar Creator (use _ as word separator, and don't bother with + yet)
* Fix the start and end with any Ultrastar editor
* `ultrastar-fix-linebreaks < sentences.txt | ultrastar-split-lyrics _ > words.txt`
* Fix start and end of the now-appeared words in any Ultrastar editor
* Manually insert + signs in words.txt (use any text editor)
* `ultrastar-split-lyrics + < words.txt > notes.txt`
* Fix start and end of the now-appeared syllables in any Ultrastar editor

You will still need to finetune here and there (for example, syllables spread across
multiple tones) but I find this to be way less tedious.

## Future
A number of additions are planned for the future, at least:

* have `check` able to also run on individual files instead of directories
