from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

emails = [
    "Win $1000 now",
    "Congratulations you won a prize",
    "FREE money click this link",
    "Meeting tomorrow at 9 AM",
    "Please send me the report",
    "Can you join the meeting tomorrow"
]
# 1 = Spam
# 0 = Normal
labels = [1, 1, 1, 0, 0, 0]
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(emails)
print(X)
model = MultinomialNB()
model.fit(X, labels)
new_email = ["Congratulations you won FREE money"]
new_X = vectorizer.transform(new_email)
prediction = model.predict(new_X)
if prediction[0] == 1:
    print(" SPAM")
else:
    print("NORMAL")