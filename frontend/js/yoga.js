document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("webcam");
  const startBtn = document.getElementById("start-btn");
  const stopBtn = document.getElementById("stop-btn");
  const captureBtn = document.getElementById("capture-btn");
  const preview = document.getElementById("webcamPreview");
  const resultBox = document.getElementById("resultBox");

  let stream;
  let capturedCanvas = null;

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
  captureBtn.addEventListener("click", () => {
    if (!video) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    preview.innerHTML = "";
    preview.appendChild(canvas);

    capturedCanvas = canvas;  // Save for uploading
  });

  // Detect pose
  document.getElementById("detectPoseBtn").addEventListener("click", async () => {
    if (!capturedCanvas) {
      alert("Please capture an image first!");
      return;
    }

    // Convert canvas → Blob → File
    capturedCanvas.toBlob(async function (blob) {
      const file = new File([blob], "capture.jpg", { type: "image/jpeg" });

      let formData = new FormData();
      formData.append("file", file);  // IMPORTANT — must match backend

      try {
        const res = await fetch("http://localhost:5000/predict", {
          method: "POST",
          body: formData
        });

        const data = await res.json();

        if (data.error) {
          alert(data.error);
        } else {
          resultBox.innerText = "Pose: " + data.pose;
        }

      } catch (err) {
        alert("Server Error! Check backend logs.");
        console.error(err);
      }
    }, "image/jpeg");
  });
});
