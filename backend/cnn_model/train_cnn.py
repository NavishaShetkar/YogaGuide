import pandas as pd
import numpy as np
import tensorflow as tf
import os
import json
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# ---------- PATH SETUP ----------
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "..",
    "pose_dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "pose_model.h5"
)

CLASS_PATH = os.path.join(
    BASE_DIR,
    "class_names.json"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "scaler.pkl"
)

# ---------- LOAD DATASET ----------
data = pd.read_csv(DATA_PATH)

# Features
X = data.iloc[:, :-1].values

# Labels
y = data.iloc[:, -1].values

# ---------- ENCODE LABELS ----------
encoder = LabelEncoder()

y = encoder.fit_transform(y)

class_names = list(encoder.classes_)

# Save class names
with open(CLASS_PATH, "w") as f:

    json.dump(class_names, f)

# ---------- FEATURE SCALING ----------
# Important because:
# coordinates ≈ -1 to 1
# angles ≈ 0 to 180

scaler = StandardScaler()

X = scaler.fit_transform(X)

# Save scaler
joblib.dump(
    scaler,
    SCALER_PATH
)

# ---------- TRAIN / TEST SPLIT ----------
X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42,

    stratify=y
)

# ---------- MODEL ----------
# Current features:
# 12 landmarks × 3 coords = 36
# 8 angles
# Total = 44

model = Sequential([

    Dense(
        256,
        activation='relu',
        input_shape=(X.shape[1],)
    ),

    Dropout(0.3),

    Dense(
        128,
        activation='relu'
    ),

    Dropout(0.3),

    Dense(
        64,
        activation='relu'
    ),

    Dense(
        32,
        activation='relu'
    ),

    Dense(
        len(np.unique(y)),
        activation='softmax'
    )
])

# ---------- COMPILE ----------
model.compile(

    optimizer='adam',

    loss='sparse_categorical_crossentropy',

    metrics=['accuracy']
)

# ---------- EARLY STOPPING ----------
early_stop = EarlyStopping(

    monitor='val_loss',

    patience=15,

    restore_best_weights=True
)

# ---------- TRAIN ----------
print(
    f"\nTraining on {X.shape[1]} features..."
)

history = model.fit(

    X_train,
    y_train,

    validation_data=(
        X_test,
        y_test
    ),

    epochs=100,

    batch_size=16,

    callbacks=[early_stop],

    verbose=1
)

# ---------- EVALUATE ----------
loss, accuracy = model.evaluate(

    X_test,
    y_test,

    verbose=0
)

print(
    f"\nTEST ACCURACY: "
    f"{round(accuracy * 100, 2)}%"
)

# ---------- SAVE MODEL ----------
model.save(MODEL_PATH)

print(
    f"\nModel saved at:\n{MODEL_PATH}"
)

print(
    f"\nScaler saved at:\n{SCALER_PATH}"
)

print(
    f"\nClass names saved at:\n{CLASS_PATH}"
)