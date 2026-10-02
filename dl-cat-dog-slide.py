import tensorflow as tf
from tensorflow.keras import layers, models
# Load images
dataset = tf.keras.utils.image_dataset_from_directory(
    "dataset",
    image_size=(180, 180),
    batch_size=32
)
# Normalize pixels: 0-255 → 0-1
normalization = layers.Rescaling(1./255)

# Create Neural Network
model = models.Sequential([
    normalization,
    
    #Horizontal edge, Vertical edge, Curve, Texture
    layers.Conv2D(32, 3, activation="relu"),
    layers.MaxPooling2D(),
    #shapes
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(),
    #patterns
    layers.Conv2D(128, 3, activation="relu"),
    layers.MaxPooling2D(),

    #Convert to Vector
    layers.Flatten(),
    #Fully Connected Layer ដែលមាន 128 neurons
    layers.Dense(128, activation="relu"),

    # Output: Cat or Dog
    layers.Dense(2, activation="softmax")
])

# Prepare training
#Adam គឺជា Optimizer ដែលប្រើដើម្បី Update Weights
#loss="sparse_categorical_crossentropy", Prediction របស់ Model ខុសពី Target ប៉ុណ្ណា?
#metrics=["accuracy"] វាប្រាប់យើងថា Model ទាយត្រូវប៉ុន្មានភាគរយ។
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)
# Train
#Epoch = ចំនួនដងដែល Model ឆ្លងកាត់ Training Dataset ទាំងមូល។
model.fit(
    dataset,
    epochs=10
)
# Save model
model.save("cat_dog_model.keras")


import tensorflow as tf
import numpy as np

# Load trained model
model = tf.keras.models.load_model("cat_dog_model.keras")
# Load image
image = tf.keras.utils.load_img(
    "dog_test.jpg",
    target_size=(180, 180)
)
# Convert image to array
image = tf.keras.utils.img_to_array(image)
# Add batch dimension
image = np.expand_dims(image, axis=0)
# Predict
prediction = model.predict(image)
# Get result
classes = ["cat", "dog"]
index = np.argmax(prediction[0])
confidence = prediction[0][index]

print("Prediction:", classes[index])
print("Confidence:", confidence)