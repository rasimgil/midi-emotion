import pandas as pd
from collections import namedtuple
import matplotlib.pyplot as plt
import os

# input_file = "./aux_data/survey.csv"
# output_file = "./aux_data/temp.csv"

# df = pd.read_csv(input_file, index_col=0)

# df.replace({"High": "H", "Low": "L"}, inplace=True)

# df.reset_index(drop=True, inplace=True)

# df.to_csv(output_file, index=False)

df = pd.read_csv("./aux_data/temp.csv")

Sample = namedtuple("Sample", ["N", "M", "A", "V"])
Answer = namedtuple("Answer", ["n", "s", "a", "v"])

samples = []
with open("./form_ordering.txt") as f:
    for line in f:
        n, rest = line.split("- ")
        model, condition = rest.split("_")
        a, v = condition[0], condition[1]
        sample = Sample(n.strip(), model, a, v)
        samples.append(sample)

answers = []
for index, row in df.iterrows():
    for i in range(1, 26):
        score = row[f"Sample {i}"]
        valence = row[f"Valence for Sample {i}"]
        arousal = row[f"Arousal for Sample {i}"]
        answer = Answer(i, score, arousal, valence)
        answers.append(answer)

answers_n = lambda n: [answer for answer in answers if answer.n == n]

results = {}
for i in range(1, 26):
    sample_answers = answers_n(i)
    valence_counts = {"H": 0, "L": 0}
    arousal_counts = {"H": 0, "L": 0}
    total = len(sample_answers)
    
    for answer in sample_answers:
        valence_counts[answer.v] += 1
        arousal_counts[answer.a] += 1
    
    valence_percentage = {key: (val / total) * 100 for key, val in valence_counts.items()}
    arousal_percentage = {key: (val / total) * 100 for key, val in arousal_counts.items()}
    
    results[i] = {
        "V": valence_percentage,
        "A": arousal_percentage
    }

def get_accuracy(i):
    sample = samples[i - 1]
    if sample.A == "N":
        return None
    result = results[i]
    acc_a = result["A"].get(sample.A, 0)
    acc_v = result["V"].get(sample.V, 0)
    return acc_a, acc_v

samples_m = lambda m: [sample for sample in samples if sample.M == m]

def get_avg_model_acc(m):
    model_samples = samples_m(m)
    acc_a = 0.0
    acc_v = 0.0
    valid_samples = 0
    
    for sample in model_samples:
        acc = get_accuracy(int(sample.N))
        if acc:
            acc_a += acc[0]
            acc_v += acc[1]
            valid_samples += 1
    
    if valid_samples > 0:
        acc_a /= valid_samples
        acc_v /= valid_samples
    
    return acc_a, acc_v

def get_model_votes(m):
    votes = []
    for sample in samples_m(m):
        answers_for_sample = answers_n(int(sample.N))
        for answer in answers_for_sample:
            votes.append(float(answer.s))
    return votes

def plot_accs(models):
    avg_accuracies = {m: get_avg_model_acc(m) for m in models}

    x = range(len(models))
    width = 0.35

    _, ax = plt.subplots()

    acc_a = [avg_accuracies[m][0] for m in models]
    acc_v = [avg_accuracies[m][1] for m in models]

    base_colors = ["lightcoral", "yellowgreen", "cornflowerblue", "plum", "khaki"]
    dark_colors = ["darkred", "darkgreen", "mediumblue", "indigo", "darkkhaki"]

    _ = ax.bar(x, acc_a, width, label="Arousal Accuracy", color=base_colors)
    _ = ax.bar([p + width for p in x], acc_v, width, label="Valence Accuracy", color=dark_colors)

    ax.set_xlabel("Models")
    ax.set_ylabel("Percentage")
    ax.set_title("Average Arousal and Valence Accuracies by Model")
    ax.set_xticks([p + width / 2 for p in x])
    ax.set_xticklabels(models)
    ax.set_ylim(0, 100)
    ax.legend()

    plt.savefig(os.path.join("./plots", "accs.png"))

def plot_votes_histogram(models):
    _, ax = plt.subplots()

    hist_data = [get_model_votes(m) for m in models]
    labels = [f"Model {m}" for m in models]

    ax.hist(hist_data, bins=[1, 2, 3, 4, 5, 6], alpha=0.7, label=labels, edgecolor="black")

    ax.set_xlabel("Score")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Votes by Model")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend()

    plt.savefig(os.path.join("./plots", "votes_histogram.png"))

if __name__ == "__main__":
    models = ["1", "5", "10", "46", "CC"]
    plot_accs(models)
    plot_votes_histogram(models)