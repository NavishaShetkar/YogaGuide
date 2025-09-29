🧘 AI-Driven Yoga Pose Detection & Correction

An AI-powered system that detects yoga poses, evaluates correctness, and provides real-time feedback using MediaPipe, OpenPose, and Deep Learning.

🚀 Features
1) Real-time pose detection from webcam
2) Compares user’s pose with reference yoga poses
3) Provides text/audio feedback (“Straighten your spine”, “Lift your arm”)
4) Supports multiple asanas (Tree Pose, Warrior Pose, Downward Dog, etc.)
5) Flask-based web application

   
🛠️ Tech Stack
1) Python 3.10+
2) TensorFlow / Keras
3) MediaPipe / OpenPose
4) Flask (for web app)
5) OpenCV, NumPy, Pandas

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
1. Clone repo:
   git clone https://github.com/YOUR-USERNAME/AI-Yoga-Pose-Detection.git
   cd AI-Yoga-Pose-Detection

2. Install dependencies:
   pip install -r requirements.txt

▶️ Run Application
> python app.py
> Then open http://127.0.0.1:5000/ in your browser.

📊 Dataset
Yoga-82: https://github.com/yoga82-dataset
Human3.6M: http://vision.imar.ro/human3.6m

📜 License

This project is open-source under the MIT License.
