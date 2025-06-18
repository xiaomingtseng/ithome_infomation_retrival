# This script calculates recall for each line in precision_recall.txt

def calculate_recall(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Skip the header line
    results = []
    for line in lines[2:]:
        if line.strip():
            tp, fn = map(int, line.split()[:2])
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            results.append(recall)

    total_tp = sum(tp for tp, fn in (map(int, line.split()[:2]) for line in lines[2:] if line.strip()))
    total_fn = sum(fn for tp, fn in (map(int, line.split()[:2]) for line in lines[2:] if line.strip()))
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    print(f"Overall Recall: {overall_recall:.2f}")

    return overall_recall

if __name__ == "__main__":
    file_path = "d:\\Github\\IR\\precision_recall.txt"
    recall = calculate_recall(file_path)

    # print result

    print(recall)