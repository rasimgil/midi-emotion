import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import mido
from argparse import ArgumentParser
import threading

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class Player:
    def play(self, file, outport):
        while True:
            try:
                midi_file = mido.MidiFile(file)
                break
            except EOFError:
                time.sleep(0.1)
        
        for msg in midi_file.play():
            outport.send(msg)

class Watcher(FileSystemEventHandler):
    def __init__(self, player, outport):
        self.player = player
        self.outport = outport

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".mid"):
            print(f"New file detected: {event.src_path}")
            self.player.play(event.src_path, self.outport)

def start_watcher(directory, player, outport):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    assert os.path.exists(directory)

    event_handler = Watcher(player, outport)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def generate_midi(model_dir, arousal, valence):
    inf_gen_script = os.path.join(root_dir, "midi-emotion", "src", "inf-gen.py")
    main_output_dir = os.path.join(root_dir, "midi-emotion", "output")
    midi_output_dir = os.path.join(main_output_dir, model_dir, "generations", "radio")
    
    if not os.path.exists(midi_output_dir):
        os.makedirs(midi_output_dir)
        print(f"Created directory: {midi_output_dir}")

    assert os.path.exists(os.path.join(main_output_dir, model_dir))

    command = [
        "python", inf_gen_script,
        "--model_dir", model_dir,
        "--conditioning", "continuous_concat",
        "--arousal", str(arousal),
        "--valence", str(valence)
    ]
    return subprocess.Popen(command, cwd=midi_output_dir)

def open_timidity_port():
    subprocess.Popen(["timidity", "-iA"])

if __name__ == "__main__":
    parser = ArgumentParser(description="Plays an infinite stream of midi events based on conditioning")
    parser.add_argument("--valence", type=float, help="Conditioning valence value", default=0)
    parser.add_argument("--arousal", type=float, help="Conditioning arousal value", default=0)
    parser.add_argument("--model_dir", type=str, help="Directory with model", required=True)
    args = parser.parse_args()

    main_output_dir = os.path.join(root_dir, "midi-emotion", "output")
    midi_output_dir = os.path.join(main_output_dir, args.model_dir, "generations", "radio")
    
    open_timidity_port()
    time.sleep(1)
    
    outport = mido.open_output(mido.get_output_names()[2])

    player = Player()
    watcher_thread = threading.Thread(target=start_watcher, args=(midi_output_dir, player, outport))
    watcher_thread.start()

    try:
        midi_process = generate_midi(args.model_dir, args.arousal, args.valence)
        watcher_thread.join()
    except KeyboardInterrupt:
        print("Stopping...")
        midi_process.terminate()
        watcher_thread.join()
