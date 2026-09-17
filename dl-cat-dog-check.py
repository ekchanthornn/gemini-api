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
print(image)
# Predict
prediction = model.predict(image)

# Get result
classes = ["cat", "dog"]

index = np.argmax(prediction[0])
confidence = prediction[0][index]

print("Prediction:", classes[index])
print("Confidence:", confidence)