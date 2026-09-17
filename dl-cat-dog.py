import tensorflow as tf
from tensorflow.keras import layers, models

# Load images
dataset = tf.keras.utils.image_dataset_from_directory(
    "dataset",
    image_size=(180, 180),
    batch_size=32
)

# Get class names
print(dataset.class_names)
# ['cat', 'dog']

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