from sklearn.tree import DecisionTreeClassifier

# ទិន្នន័យលក្ខណៈសម្គាល់ (Features): [ear_size, face_roundness, snout_length]

X = [
    [8, 9, 3],   # ឆ្មា
    [9, 8, 3],   # ឆ្មា
    [7, 9, 2],   # ឆ្មា
    [3, 5, 8],   # ឆ្កែ
    [4, 4, 9],   # ឆ្កែ
    [3, 6, 7],   # ឆ្កែ
]

# លទ្ធផលគោលដៅ (Labels): 0 = ឆ្មា, 1 = ឆ្កែ
y = [0, 0, 0, 1, 1, 1]

# បង្កើត ML Model
model = DecisionTreeClassifier()

# បង្រៀនម៉ាស៊ីន (Train)
model.fit(X, y)

# សាកល្បងយករូបសត្វថ្មីមួយមកទស្សន៍ទាយ
new_animal = [
    [8, 8, 3]
]

# ឲ្យម៉ាស៊ីនទាយ (Predict)
prediction = model.predict(new_animal)

if prediction[0] == 0:
    print("ឆ្មា")
else:
    print("ឆ្កែ")