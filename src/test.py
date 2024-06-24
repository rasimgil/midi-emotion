import mido 

mid = mido.MidiFile("./Chromatic_scale_ascending_on_C.mid")
mid1 = mido.MidiFile("./Chromatic_scale_descending_on_C.mid")

outport = mido.open_output(mido.get_output_names()[2])

l = [mid, mid1]

for m in l:
    for msg in m.play():
        outport.send(msg)

