function showUpload() {
    document.getElementById("uploadSection").style.display = "block";
    document.getElementById("webcamSection").style.display = "none";
}

function showWebcam() {
    document.getElementById("uploadSection").style.display = "none";
    document.getElementById("webcamSection").style.display = "block";

    const video = document.getElementById("webcam");
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            alert("Webcam access denied!");
        });
}

function detectPose(mode) {
    alert("Detecting pose from " + mode + " input...");
    // TODO: Connect with Flask backend API
}

function captureImage() {
    const video = document.getElementById("webcam");
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
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