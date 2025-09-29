🧘 AI-Driven Yoga Pose Detection & Correction

An AI-powered system that detects yoga poses, evaluates correctness, and provides real-time feedback using MediaPipe, OpenPose, and Deep Learning.

🚀 Features
Real-time pose detection from webcam
Compares user’s pose with reference yoga poses
Provides text/audio feedback (“Straighten your spine”, “Lift your arm”)
Supports multiple asanas (Tree Pose, Warrior Pose, Downward Dog, etc.)
Flask-based web application
🛠️ Tech Stack
Python 3.10+
TensorFlow / Keras
MediaPipe / OpenPose
Flask (for web app)
OpenCV, NumPy, Pandas
📂 Project Structure
AI-Yoga-Pose-Detection/
│── app.py                # Flask app
│── requirements.txt       # Python dependencies
│── yoga_pose_detection.ipynb  # Model experiments
│── /models/              # Saved ML models
│── /datasets/            # Yoga datasets
│── /static/              # CSS, JS, Images
│── /templates/           # HTML templates
│── /utils/               # Preprocessing & helper scripts
│── /docs/                # Documentation

🔧 Installation
Clone repo:
git clone https://github.com/YOUR-USERNAME/AI-Yoga-Pose-Detection.git
cd AI-Yoga-Pose-Detection

Install dependencies:
pip install -r requirements.txt

▶️ Run Application
python app.py


Then open http://127.0.0.1:5000/ in your browser.

📊 Dataset
Yoga-82: https://github.com/yoga82-dataset
Human3.6M: http://vision.imar.ro/human3.6m
📜 License

This project is open-source under the MIT License.
