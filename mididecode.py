import mido, sys

def note_to_name(note):
    letter = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][note % 12]
    number = (note - 12) // 12
    return str(letter) + str(number)

infile = mido.MidiFile(sys.argv[1])

notes_on = set()

for n, msg in enumerate(infile.tracks[0]):
    try:
        if msg.channel == 0:
            returns = "\n" * msg.time
            print(returns, end="")
            if msg.velocity == 0:
                note_name = note_to_name(msg.note)
                notes_on.discard(note_name)
            else:
                if note_name not in notes_on:
                    print(note_name, end=" ")
                    notes_on.add(note_name)
    except:
        pass
