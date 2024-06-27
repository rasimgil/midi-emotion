import os
import mido
import matplotlib.pyplot as plt
import pstats
import seaborn as sns
import numpy as np


def get_midi_length(file_path):
    mid = mido.MidiFile(file_path)
    total_time = 0

    for track in mid.tracks:
        absolute_time = 0
        for msg in track:
            if not msg.is_meta:
                absolute_time += msg.time
        total_time = max(total_time, absolute_time)

    ticks_per_beat = mid.ticks_per_beat
    tempo = 500000
    for msg in mid:
        if msg.type == "set_tempo":
            tempo = msg.tempo

    time_in_seconds = (total_time / ticks_per_beat) * (tempo / 1000000)
    return time_in_seconds

def get_midi_lengths_in_directory(directory_path):
    lengths = []
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith(".mid") or file_name.lower().endswith(".midi"):
            file_path = os.path.join(directory_path, file_name)
            try:
                length = get_midi_length(file_path)
                lengths.append(length)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    return lengths

def plot_histogram(lengths_dict, model_name, gen_time=None, bins=60, save_dir="./plots"):
    for subdir, lengths in lengths_dict.items():
        average_length = np.mean(lengths)
        plt.hist(lengths, bins=bins, alpha=0.5, label=f"{subdir} (Avg: {average_length:.2f}s)", histtype="step", linewidth=1.5)

    if gen_time is not None:
        plt.axvline(x=gen_time, color="r", linestyle="--", label=f"Generation time: {gen_time:.2f} s")

    plt.xlabel("Length in seconds")
    plt.ylabel("Number of MIDI files")
    plt.title(model_name)
    plt.legend()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(os.path.join(save_dir, f"{model_name}_histogram.png"))
    plt.close()

def plot_kde(lengths_dict, model_name, gen_time=None, save_dir="./plots"):
    for subdir, lengths in lengths_dict.items():
        average_length = np.mean(lengths)
        sns.kdeplot(lengths, label=f"{subdir} (Avg: {average_length:.2f}s)", linewidth=1)

    if gen_time is not None:
        plt.axvline(x=gen_time, color="r", linestyle="--", label=f"Generation time: {gen_time:.2f} s")

    plt.xlabel("Length in seconds")
    plt.ylabel("Density")
    plt.title(model_name)
    plt.legend()
    plt.xlim(left=0)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(os.path.join(save_dir, f"{model_name}_kde.png"))
    plt.close()

def get_generate_method_time(profile_path):
    p = pstats.Stats(profile_path)
    for func, stats in p.stats.items():
        if "generate.py" in func[0] and "generate" in func[2]:
            return stats[3]
    return None

def get_num_params(log_path):
    with open(log_path, "r") as file:
        for line in file:
            if line.startswith("#params ="):
                return int(line.split("=")[1].strip())
    return None

def plot_time_vs_params(model_names, params_dict, time_dict, save_dir="./plots"):
    sizes = [params_dict[model] / 1e6 for model in model_names]
    times = [time_dict[model] for model in model_names]

    plt.figure(figsize=(10, 6))
    plt.scatter(sizes, times)
    for i, size in enumerate(sizes):
        plt.annotate(model_names[i], (size, times[i]), textcoords="offset points", xytext=(0,5), ha="center")

    plt.xlabel("Number of Parameters (Millions)")
    plt.ylabel("Generation Time (s)")
    plt.title("Model Size vs. Generation Time")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(os.path.join(save_dir, "time_vs_params.png"))
    plt.close()



models = [
    "conditional1",
    "conditional5",
    "conditional10",
    "conditional46",
    "continuous_concat"
]

def main():
    params_dict = {}
    time_dict = {}

    for model in models:
        log_path = f"../output/{model}/log.txt"
        profile_path = f"./aux_data/gen_profiles/{model}_gen.prof"
        samples_dir = f"../output/{model}/generations/samples"
        
        params = get_num_params(log_path)
        gen_time = get_generate_method_time(profile_path)
        
        if params is not None and gen_time is not None:
            params_dict[model] = params
            time_dict[model] = gen_time
        
        subdirs = [d for d in os.listdir(samples_dir) if os.path.isdir(os.path.join(samples_dir, d))]
        lengths_dict = {}
        for subdir in subdirs:
            subdir_path = os.path.join(samples_dir, subdir)
            lengths_dict[subdir] = get_midi_lengths_in_directory(subdir_path)
        
        plot_histogram(lengths_dict, model, gen_time)
        plot_kde(lengths_dict, model, gen_time)

    plot_time_vs_params(models, params_dict, time_dict)

if __name__ == "__main__":
    main()
