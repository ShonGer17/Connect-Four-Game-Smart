import numpy as np
from keras.src.layers import BatchNormalization, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, Dense



model = Sequential()
model.add(Conv2D(64, (3, 3), activation='relu', input_shape=(6, 7, 1), padding='same'))
model.add(BatchNormalization()) # BN אחרי שכבה ראשונה
model.add(Conv2D(128, (3, 3), activation='relu', padding='same'))
model.add(BatchNormalization()) # BN אחרי שכבה שנייה
model.add(Conv2D(128, (2, 2), activation='relu', padding='same')) # שכבת קונבולוציה שלישית
model.add(BatchNormalization()) # BN אחרי שכבה שלישית
model.add(Flatten())
model.add(Dense(128, activation='relu')) # שומרים על 128 כדי לא להגזים
model.add(BatchNormalization()) # BN אחרי שכבה שלישית
model.add(Dropout(0.4)) # Dropout גבוה יותר
model.add(Dense(64, activation='relu'))
model.add(Dense(1, activation='sigmoid')) # שכבת יציאה
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_absolute_error'])


x_train = np.load("x_train.npy")
y_train = np.load("y_train.npy")
x_test = np.load("x_test.npy")
y_test = np.load("y_test.npy")

print(x_train.shape[0]+x_test.shape[0])

# import matplotlib.pyplot as plt
# plt.hist(y_train, bins=50)
# plt.show()



# print(x_train.shape)
# print(x_test.shape)
#
# print(x_train[0].reshape(6,7))  # האם יש בו ערכים כמו 1, -1, 0?
# print(y_train[0])               # האם הוא גבוה כשהמהלך טוב?



# # אימון המודל
history = model.fit(x_train, y_train, validation_split=0.2, epochs=10, batch_size=32)
np.save('training_history5.npy', history.history)

# הערכת המודל
score = model.evaluate(x_test, y_test, verbose=0)
print(f'Test loss (MSE): {score[0]}')
print(f'Test MAE: {score[1]}')
model.save('modelCnn5.keras')


print(x_train[0])
print()