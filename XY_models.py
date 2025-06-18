import numpy as np
from sklearn.model_selection import train_test_split
import json
import random
import matplotlib.pyplot as plt



with open('results_game.json', 'r') as json_file:
    data_dict_from_json = json.load(json_file)


def string_to_board(string):
    return np.array([int(char) for char in string]).reshape((6, 7))



# מיון לפי ציון
scores_0_0, scores_1_0, scores_others = [], [], []
for key, value in data_dict_from_json.items():
    score = value[0]
    if score == 0.0:
        scores_0_0.append((key, score))
    elif score == 1.0:
        scores_1_0.append((key, score))
    else:
        scores_others.append((key, score))



# איזון לפי הקבוצה הגדולה ביותר
target_sample_size = max(len(scores_0_0), len(scores_1_0), len(scores_others))
sampled_0_0 = random.choices(scores_0_0, k=target_sample_size) if scores_0_0 else []
sampled_1_0 = random.choices(scores_1_0, k=target_sample_size) if scores_1_0 else []
sampled_others = random.choices(scores_others, k=target_sample_size) if scores_others else []


sampled_data = sampled_0_0 + sampled_1_0 + sampled_others
random.shuffle(sampled_data)


x_raw = [item[0] for item in sampled_data]
y_raw = [item[1] for item in sampled_data]



print(f"Sampled counts: 0.0: {sum(1 for _, s in sampled_data if s == 0.0)}, "
      f"1.0: {sum(1 for _, s in sampled_data if s == 1.0)}, "
      f"0.5: {sum(1 for _, s in sampled_data if s == 0.5)}")


x = np.array([string_to_board(board_str) for board_str in x_raw])
y = np.array(y_raw)


X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)


print(f"X_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"X_test shape: {X_test.shape}")
print(f"y_test shape: {y_test.shape}")


def save_numpy(x, y, x_filename, y_filename):
    np.save(x_filename, x)
    np.save(y_filename, y)
    print(f"Saved: {x_filename}, {y_filename}")


save_numpy(X_test, y_test, "x_test.npy", "y_test.npy")
save_numpy(X_train, y_train, "x_train.npy", "y_train.npy")


plt.hist(y, bins=50)
plt.title('Y Score Distribution')
plt.xlabel('Score')
plt.ylabel('Frequency')
plt.show()
