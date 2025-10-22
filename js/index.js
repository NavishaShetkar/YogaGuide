function showUpload() {
    document.getElementById("uploadSection").style.display = "block";
    document.getElementById("webcamSection").style.display = "none";
}

function showWebcam() {
    document.getElementById("uploadSection").style.display = "none";
    document.getElementById("webcamSection").style.display = "block";

    const video = document.getElementById("webcam");
    // Webcam access only works on localhost or HTTPS
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            alert("Webcam access denied! (Ensure you are on a local server or HTTPS)");
        });
}

// --- UPDATED CORE LOGIC for Backend Communication ---
async function detectPose(mode) {
    const previewDiv = document.getElementById(mode === 'upload' ? "uploadPreview" : "webcamPreview");
    const mediaElement = previewDiv.querySelector('img, video, canvas');

    if (!mediaElement) {
        alert("Please upload a file or capture a webcam image first.");
        return;
    }

    let formData = new FormData();
    let fileBlob = null;
    let fileName = null;

    if (mode === 'upload') {
        const fileInput = document.getElementById("fileInput");
        const file = fileInput.files[0];
        if (!file) return;
        formData.append('file', file);
        fileName = file.name;
    } else if (mode === 'webcam') {
        // Convert canvas data to a Blob (file-like object)
        const canvas = mediaElement;
        fileBlob = await new Promise(resolve => {
            canvas.toBlob(resolve, 'image/png');
        });
        formData.append('file', fileBlob, 'webcam_capture.png');
        fileName = 'webcam_capture.png';
    }

    alert(`Sending ${fileName} to the backend for pose detection... (TODO: Connect with Flask backend API)`);
    
    // TODO: Replace this simulated alert with actual fetch logic to your Flask backend
    /*
    try {
        const response = await fetch('/api/detect_pose', {
            method: 'POST',
            body: formData,
        });

        // ... handle response and display processed image/video ...

    } catch (e) {
        alert(`Pose detection failed: ${e.message}`);
    }
    */
}

function captureImage() {
    const video = document.getElementById("webcam");
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    // Clear previous webcam preview and show the captured canvas
    document.getElementById("webcamPreview").innerHTML = "";
    document.getElementById("webcamPreview").appendChild(canvas);
}

document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    if (fileInput) {
        fileInput.addEventListener("change", (event) => {
            const file = event.target.files[0];
            if (file) {
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
                document.getElementById("uploadPreview").innerHTML = "";
                document.getElementById("uploadPreview").appendChild(preview);
            }
        });
    }
});