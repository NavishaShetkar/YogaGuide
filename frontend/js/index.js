let capturedCanvas = null;

// SWITCH SECTIONS
function showUpload() {
    document.getElementById("uploadSection").style.display = "block";
    document.getElementById("webcamSection").style.display = "none";
}

function showWebcam() {
    document.getElementById("uploadSection").style.display = "none";
    document.getElementById("webcamSection").style.display = "block";
}

// ===========================
// SHOW UPLOADED IMAGE PREVIEW
// ===========================
document.getElementById("fileInput").addEventListener("change", function () {
    const file = this.files[0];
    const previewBox = document.getElementById("uploadPreview");

    previewBox.innerHTML = ""; // Clear previous preview

    if (file) {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = "300px";
        img.style.marginTop = "10px";
        img.style.borderRadius = "10px";
        img.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";

        previewBox.appendChild(img);
    }
});

// ----------------------------
//  FILE UPLOAD DETECTION
// ----------------------------
document.getElementById("uploadDetectBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) return alert("Please select an image!");

    let formData = new FormData();
    formData.append("file", file);

    uploadToBackend(formData);
});


/* ----------------------------
   WEBCAM LOGIC (UPDATED)
---------------------------- */

let streaming = false;
let streamInterval = null;

document.getElementById("start-btn").addEventListener("click", async () => {
    const video = document.getElementById("webcam");

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });

        video.srcObject = stream;
        streaming = true;

        startLiveDetection(video);

    } catch (error) {
        alert("Cannot access webcam.");
        console.error(error);
    }
});

document.getElementById("stop-btn").addEventListener("click", () => {
    const video = document.getElementById("webcam");

    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }

    streaming = false;

    if (streamInterval) clearInterval(streamInterval);
});

// LIVE DETECTION EVERY 1 SECOND
function startLiveDetection(video) {
    const resultBox = document.getElementById("resultBox");

    streamInterval = setInterval(() => {
        if (!streaming) return;

        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0);

        canvas.toBlob(async (blob) => {
            let formData = new FormData();
            formData.append("file", blob, "live.jpg");

            try {
                const res = await fetch("http://127.0.0.1:5000/predict", {
                    method: "POST",
                    body: formData
                });

                const data = await res.json();

                if (data.error) {
                    resultBox.innerHTML = "⚠ " + data.error;
                } else {
    resultBox.innerHTML = `
        <h3>🧘 Live Pose</h3>
        <p><b>Pose:</b> ${data.pose}</p>
    `;

    // ⭐ ADD ANGLES HERE
    if (data.angles) {
        resultBox.innerHTML += `
            <h4>📐 Joint Angles</h4>
            <p>Left Knee: ${data.angles.left_knee}°</p>
            <p>Right Knee: ${data.angles.right_knee}°</p>
            <p>Left Elbow: ${data.angles.left_elbow}°</p>
            <p>Right Elbow: ${data.angles.right_elbow}°</p>
        `;
    }
}

            } catch (err) {
                resultBox.innerHTML = "⚠ Server Error";
            }

        }, "image/jpeg");

    }, 1000); // detect every 1 sec
}




// ----------------------------
//  SEND TO BACKEND
// ----------------------------
async function uploadToBackend(formData) {
    const resultBox = document.getElementById("resultBox");
    resultBox.style.display = "block";
    resultBox.innerHTML = "⏳ Detecting pose...";

    try {
        const res = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        console.log("SERVER RESPONSE:", data);

        if (data.error) {
    resultBox.innerHTML = "⚠ " + data.error;

} else {
    resultBox.innerHTML = `
        <h3>🧘 Live Pose</h3>
        <p><b>Pose:</b> ${data.pose}</p>
    `;

    // ⭐ SHOW ANGLES IF AVAILABLE
    if (data.angles) {
        resultBox.innerHTML += `
            <h4>📐 Joint Angles</h4>
            <p>Left Knee: ${data.angles.left_knee}°</p>
            <p>Right Knee: ${data.angles.right_knee}°</p>
            <p>Left Elbow: ${data.angles.left_elbow}°</p>
            <p>Right Elbow: ${data.angles.right_elbow}°</p>
            <p>Left Shoulder: ${data.angles.left_shoulder}°</p>
            <p>Right Shoulder: ${data.angles.right_shoulder}°</p>
        `;
    }
}

    } catch (err) {
        resultBox.innerHTML = "⚠ Server Error — check backend";
    }
}
