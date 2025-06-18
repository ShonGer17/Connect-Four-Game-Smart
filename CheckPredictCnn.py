import tensorflow as tf
import numpy as np
from matplotlib import pyplot as plt



model = tf.keras.models.load_model('modelCnn5.keras')
history = np.load('training_history5.npy', allow_pickle=True).item()


plt.plot(history['loss'], label='Training Loss')
plt.plot(history['val_loss'], label='Validation Loss')
plt.title('Model Loss During Training')
plt.xlabel('Epochs')
plt.ylabel('MSE Loss')
plt.legend()
plt.show()


plt.plot(history['mean_absolute_error'], label='Training MAE')
plt.plot(history['val_mean_absolute_error'], label='Validation MAE')
plt.title('Mean Absolute Error During Training')
plt.xlabel('Epochs')
plt.ylabel('MAE')
plt.legend()
plt.show()



def board_str_to_numpy(board_str):
    if len(board_str) != 42:
        print("הסטרינג חייב להיות באורך 42 תווים (6 שורות × 7 טורים)")

    board = np.array([int(char) for char in board_str])

    board = board.reshape((6, 7))

    board = board[np.newaxis, :, :]  # צורה סופית: (1, 6, 7)

    return board



board_str1 = "000000000000000000000000000000200200011112"
board_str2 = "000000000000002000000100000010020002211112"
board_str3 = "000000000000000000000000000100200122221111"
board_str4 = "000000000000000000000000000100200122221111"
board_str5 = "000000000000000000000000000000100100022221"
board_str6 = "000000000000000000000000000200100211112222"
board_str7 = "112221222111211112121222121211212121212221"
board_np1 = board_str_to_numpy(board_str1)
board_np2 = board_str_to_numpy(board_str2)
board_np3 = board_str_to_numpy(board_str3)
board_np4 = board_str_to_numpy(board_str4)
board_np5 = board_str_to_numpy(board_str5)
board_np6 = board_str_to_numpy(board_str6)
board_np7 = board_str_to_numpy(board_str7)


prediction1 = model.predict(board_np1)
print("game 1:")
print(prediction1)


prediction2 = model.predict(board_np2)
print("game 2:")
print(prediction2)


prediction3 = model.predict(board_np3)
print("game 3:")
print(prediction3)


prediction4 = model.predict(board_np4)
print("game 4:")
print(prediction4)


prediction5 = model.predict(board_np5)
print("game 5:")
print(prediction5)


prediction6 = model.predict(board_np6)
print("game 6:")
print(prediction6)


prediction7 = model.predict(board_np7)
print("game 7:")
print(prediction7)