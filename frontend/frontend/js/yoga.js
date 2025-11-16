document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("webcam");
  const startBtn = document.getElementById("start-btn");
  const stopBtn = document.getElementById("stop-btn");
  const captureBtn = document.getElementById("capture-btn");
  const preview = document.getElementById("webcamPreview");

  let stream;

  if (!video || !startBtn || !stopBtn) return;

  // Start webcam
  startBtn.addEventListener("click", () => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(s => {
        stream = s;
        video.srcObject = s;
      })
      .catch(err => {
        alert("Webcam access denied or unavailable!");
        console.error(err);
      });
  });

  // Stop webcam
  stopBtn.addEventListener("click", () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      video.srcObject = null;
    }
  });

  // Capture snapshot
  if (captureBtn) {
    captureBtn.addEventListener("click", () => {
      if (!video || !preview) return;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0);
      preview.innerHTML = "";
      preview.appendChild(canvas);
    });
  }
});

// Detect Pose (future backend integration)
function detectPose() {
  alert("Analyzing your live yoga pose...");
  // TODO: Connect to Flask backend API
}