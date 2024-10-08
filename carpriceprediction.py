
# Importing Libraries

import tensorflow as tf #models
import seaborn as sns #visuals
from tensorflow.keras.layers import Normalization, Dense, InputLayer
import pandas as pd
from tensorflow.keras.losses import MeanAbsoluteError
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt #visuals
import numpy as np


"""# **DATA** **PREPARATION**

## Importing Dataset
"""

data  = pd.read_csv('train.csv')
data.head()

##Visualising dataset

sns.pairplot(data[['years', 'km', 'rating', 'condition', 'economy', 'top speed', 'hp', 'torque', 'current price']], diag_kind='kde')

"""##Converting pd.DataFrame to Tensor"""

tensorData = tf.constant(data)
tensorData = tf.cast(tensorData, tf.float64)
print(tensorData[:5])

"""##Shuffling the order of dataset"""

tensorData = tf.random.shuffle(tensorData)
print(tensorData[:5])

"""##Splitting Dataset into Features and Labels"""

X = tensorData[:, 3:-1]
print(X[:5])

y = tensorData[:, -1]
print(y.shape)
y = tf.expand_dims(y, axis=-1)
print(y.shape)

"""##Splitting Dataset into Train Dataset, Validation Dataset, Test Dataset

"""

TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1
DATASET_SIZE = len(X)

X_train = X[:int(TRAIN_RATIO * DATASET_SIZE)]
y_train = y[:int(TRAIN_RATIO * DATASET_SIZE)]
print(X_train.shape, y_train.shape)

train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
train_dataset = train_dataset.shuffle(buffer_size=len(X_train),reshuffle_each_iteration=True).batch(32).prefetch(tf.data.AUTOTUNE)
train_dataset.element_spec

X_val = X[int(DATASET_SIZE * TRAIN_RATIO):int(DATASET_SIZE * (TRAIN_RATIO + VAL_RATIO))]
y_val = y[int(DATASET_SIZE * TRAIN_RATIO):int(DATASET_SIZE * (TRAIN_RATIO + VAL_RATIO))]
print(X_val.shape, y_val.shape)

val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val))
val_dataset = val_dataset.shuffle(buffer_size=8, reshuffle_each_iteration=True).batch(32).prefetch(tf.data.AUTOTUNE)
val_dataset.element_spec

X_test = X[int(DATASET_SIZE * (TRAIN_RATIO + VAL_RATIO)):]
y_test = y[int(DATASET_SIZE * (TRAIN_RATIO + VAL_RATIO)):]
print(X_test.shape, y_test.shape)

test_dataset = tf.data.Dataset.from_tensor_slices((X_test, y_test))
test_dataset = test_dataset.shuffle(buffer_size=8, reshuffle_each_iteration=True).batch(32).prefetch(tf.data.AUTOTUNE)
test_dataset.element_spec

"""##Normalizing Data"""

normalizer = Normalization()
normalizer.adapt(X)
X_normalized = normalizer(X)

"""#MODEL CREATION"""

model = tf.keras.Sequential([
    InputLayer(input_shape =(8,)),
    normalizer,
    Dense(512, activation='relu'),
    Dense(512, activation='relu'),
    Dense(256, activation='relu'),
    Dense(1, activation='linear')
])
model.summary()

tf.keras.utils.plot_model(model, to_file='model.png', show_shapes=True)

"""##Compiling Model"""

model.compile(optimizer=Adam(learning_rate=0.001),
              loss=MeanAbsoluteError())

history = model.fit(train_dataset, validation_data=val_dataset, epochs=100, verbose=1)

"""##Plotting loss and Val_loss"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.legend(['loss', 'val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.show()

"""##Evaluating Model"""

model.evaluate(X_test, y_test)

"""#PREDICTION"""

y_pred = list(model.predict(X_test)[:,0])
y_true = list(y_test[:,0].numpy())
print(y_pred, '\n', y_true)

plt.plot(y_pred,color='b')
plt.plot(y_true,color='r')
plt.legend(['y_pred', 'y_true'])
plt.show()

"""#Checking accuracy of model"""

y_true = np.array(y_true)
y_pred = np.array(y_pred)

mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
print(f'Mean Absolute Percentage Error (MAPE): {mape}%')

model.save('CarPricePrediction.keras')

"""#Main"""

def main():
    # Load the trained model
    model = tf.keras.models.load_model('CarPricePrediction.keras')

    # Prompt user for input
    years = float(input("Enter years: "))
    km = float(input("Enter kilometers: "))
    rating = float(input("Enter rating: "))
    condition = float(input("Enter condition: "))
    economy = float(input("Enter economy: "))
    top_speed = float(input("Enter top speed: "))
    hp = float(input("Enter horsepower: "))
    torque = float(input("Enter torque: "))

    # Create a TensorFlow constant from user input
    test_input = tf.constant([[years, km, rating, condition, economy, top_speed, hp, torque]], dtype=tf.float64)

    # Predict the value
    prediction = model.predict(test_input)

    # Calculate the margin of error based on MAPE
    margin_of_error = prediction[0][0] * (mape / 100)

    # Print the prediction with the margin of error
    print("Predicted Value: {:.2f} ± {:.2f}".format(prediction[0][0], margin_of_error))

if __name__ == "__main__":
    main()
