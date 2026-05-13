import pandas as pd
import numpy as np
import tensorflow as tf
import os
import json
import joblib

from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

# ==========================================
# GPU MEMORY FIX
# ==========================================
gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:

    try:

        for gpu in gpus:

            tf.config.experimental.set_memory_growth(
                gpu,
                True
            )

    except RuntimeError as e:

        print(f"GPU Error: {e}")

# ==========================================
# PATH SETUP
# ==========================================
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

# ==========================================
# LOAD DATASET
# ==========================================
print("\nLoading dataset...")

data = pd.read_csv(DATA_PATH)

print(f"Dataset Shape: {data.shape}")

# ==========================================
# FEATURES & LABELS
# ==========================================
X = data.iloc[:, :-1].values

y = data.iloc[:, -1].values

print(f"Feature Shape: {X.shape}")

# ==========================================
# LABEL ENCODING
# ==========================================
encoder = LabelEncoder()

y = encoder.fit_transform(y)

class_names = list(
    encoder.classes_
)

# ==========================================
# SHOW CLASS DISTRIBUTION
# ==========================================
print("\nClass Distribution:")

print(Counter(y))

# ==========================================
# SAVE CLASS NAMES
# ==========================================
with open(CLASS_PATH, "w") as f:

    json.dump(
        class_names,
        f
    )

# ==========================================
# FEATURE SCALING
# ==========================================
print("\nScaling features...")

scaler = StandardScaler()

X = scaler.fit_transform(X)

# SAVE SCALER
joblib.dump(
    scaler,
    SCALER_PATH
)

print("Scaler saved successfully")

# ==========================================
# TRAIN TEST SPLIT
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42,

    stratify=y
)

print(f"\nTraining Samples: {len(X_train)}")

print(f"Testing Samples: {len(X_test)}")

# ==========================================
# MODEL
# ==========================================
# Current Features:
#
# 14 landmarks × 3 coords = 42
#
# 14 angles
#
# Total = 56 Features

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

# ==========================================
# OPTIMIZER
# ==========================================
optimizer = Adam(

    learning_rate=0.0005
)

# ==========================================
# COMPILE
# ==========================================
model.compile(

    optimizer=optimizer,

    loss='sparse_categorical_crossentropy',

    metrics=['accuracy']
)

# ==========================================
# EARLY STOPPING
# ==========================================
early_stop = EarlyStopping(

    monitor='val_loss',

    patience=15,

    restore_best_weights=True
)

# ==========================================
# TRAIN
# ==========================================
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

# ==========================================
# EVALUATE
# ==========================================
print("\nEvaluating model...")

loss, accuracy = model.evaluate(

    X_test,
    y_test,

    verbose=0
)

print(
    f"\nTEST ACCURACY: "
    f"{round(accuracy * 100, 2)}%"
)

# ==========================================
# SAVE MODEL
# ==========================================
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

# ==========================================
# FINAL INFO
# ==========================================
print("\n===================================")

print("TRAINING COMPLETED SUCCESSFULLY")

print("===================================")

print("\nFeature Summary:")

print("42 landmark coordinates")

print("14 body angles")

print("56 total features")

print("\nYou can now run:")

print("\npython app.py")
