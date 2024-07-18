import mido 
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

data_dir = os.path.join(root_dir, "midi-emotion", "src", "aux_data", )
mid_path = os.path.join(data_dir, "Chromatic_scale_ascending_on_C.mid")
mid1_path = os.path.join(data_dir, "Chromatic_scale_descending_on_C.mid")
mid = mido.MidiFile(mid_path)
mid1 = mido.MidiFile(mid1_path)

outport = mido.open_output(mido.get_output_names()[2])

l = [mid, mid1]

for m in l:
    for msg in m.play():
        outport.send(msg)

