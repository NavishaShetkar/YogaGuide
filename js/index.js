// Show Upload Section
function showUpload() {
  const upload = document.getElementById("uploadSection");
  const webcam = document.getElementById("webcamSection");

  upload.style.display = "block";
  webcam.style.display = "none";

  // Stop webcam if active
  const video = document.getElementById("webcam");
  if (video.srcObject) {
    video.srcObject.getTracks().forEach(track => track.stop());
    video.srcObject = null;
  }
}

// Show Webcam Section
function showWebcam() {
  const upload = document.getElementById("uploadSection");
  const webcam = document.getElementById("webcamSection");

  upload.style.display = "none";
  webcam.style.display = "block";

  const video = document.getElementById("webcam");
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
    })
    .catch(err => {
      alert("Webcam access denied or not available!");
      console.error(err);
    });
}

// Capture a Frame from Webcam
function captureImage() {
  const video = document.getElementById("webcam");
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);
  document.getElementById("webcamPreview").innerHTML = "";
  document.getElementById("webcamPreview").appendChild(canvas);
}

// Detect Pose (placeholder)
function detectPose(mode) {
  const button = event.target;
  button.textContent = "Detecting...";
  button.disabled = true;

  setTimeout(() => {
    alert(`Pose detection simulated for: ${mode}`);
    button.textContent = "Detect Pose";
    button.disabled = false;
  }, 1500); // Fake delay to mimic backend processing
}

// File Upload Preview
document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput) return;

  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    let preview;

    if (file.type.startsWith("video/")) {
      preview = document.createElement("video");
      preview.controls = true;
    } else {
      preview = document.createElement("img");
    }

    preview.src = url;
    preview.width = 400;
    preview.style.borderRadius = "10px";
    preview.style.marginTop = "15px";

    document.getElementById("uploadPreview").innerHTML = "";
    document.getElementById("uploadPreview").appendChild(preview);
  });
});
