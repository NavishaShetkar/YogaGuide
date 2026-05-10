document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       LOAD USER PROFILE
    ========================= */

    async function loadUserProfile() {

        const user_id = localStorage.getItem("user_id");

        if (!user_id) {

            window.location.href = "login.html";

            return;
        }

        const res = await fetch(
            `http://127.0.0.1:5000/get_profile/${user_id}`
        );

        const data = await res.json();

        if (data.error) {

            console.log("No profile found");

            return;
        }

        document.getElementById("name").innerText =
            data.full_name;

        document.getElementById("age").innerText =
            data.age;

        document.getElementById("gender").innerText =
            data.gender;

        document.getElementById("goal").innerText =
            data.goal;

        document.getElementById("experience").innerText =
            data.experience;
    }

    loadUserProfile();

    /* =========================
       SWITCH SECTIONS
    ========================= */

    window.showUpload = () => {

        document.getElementById(
            "uploadSection"
        ).style.display = "block";

        document.getElementById(
            "webcamSection"
        ).style.display = "none";
    };

    window.showWebcam = () => {

        document.getElementById(
            "uploadSection"
        ).style.display = "none";

        document.getElementById(
            "webcamSection"
        ).style.display = "block";
    };

    /* =========================
       ELEMENTS
    ========================= */

    const fileInput =
        document.getElementById("fileInput");

    const uploadBtn =
        document.getElementById("uploadDetectBtn");

    const previewBox =
        document.getElementById("uploadPreview");

    const webcamStream =
        document.getElementById("webcamStream");

    const startBtn =
        document.getElementById("start-btn");

    const stopBtn =
        document.getElementById("stop-btn");

    const uploadResult =
        document.getElementById("uploadResult");

    const user_id =
        localStorage.getItem("user_id");

    let poseInterval = null;

    /* =========================
       LIVE RESULT ELEMENTS
    ========================= */

    const poseText =
        document.getElementById("poseText");

    const confidenceText =
        document.getElementById("confidenceText");

    const recommendationText =
        document.getElementById("recommendationText");

    const correctionText =
        document.getElementById("correctionText");

    /* =========================
       UPLOAD RESULT ELEMENTS
    ========================= */

    const uploadPoseText =
        document.getElementById("uploadPoseText");

    const uploadConfidenceText =
        document.getElementById("uploadConfidenceText");

    /* =========================
       IMAGE PREVIEW
    ========================= */

    if (fileInput) {

        fileInput.addEventListener("change", () => {

            previewBox.innerHTML = "";

            const file = fileInput.files[0];

            if (file) {

                const img =
                    document.createElement("img");

                img.src =
                    URL.createObjectURL(file);

                img.style.maxWidth = "300px";

                img.style.borderRadius = "12px";

                img.style.marginTop = "15px";

                previewBox.appendChild(img);
            }
        });
    }

    /* =========================
       IMAGE UPLOAD
    ========================= */

    if (uploadBtn) {

        uploadBtn.addEventListener("click", async () => {

            const file = fileInput.files[0];

            if (!file) {

                alert("Please select an image!");

                return;
            }

            const formData = new FormData();

            formData.append("file", file);

            await sendToBackend(formData);
        });
    }

    /* =========================
       START WEBCAM
    ========================= */

    if (startBtn) {

        startBtn.addEventListener("click", () => {

            webcamStream.src =
                "http://127.0.0.1:5000/video_feed";

            if (poseInterval)
                clearInterval(poseInterval);

            // ---------- FETCH LIVE DATA ----------
            poseInterval = setInterval(async () => {

                try {

                    const res = await fetch(
                        `http://127.0.0.1:5000/get_pose/${user_id}`
                    );

                    const data = await res.json();

                    // ---------- UPDATE UI ----------
                    poseText.innerText =
                        data.pose;

                    confidenceText.innerText =
                        `${data.confidence}%`;

                    recommendationText.innerText =
                        data.recommendation;

                    correctionText.innerText =
                        data.correction || "---";

                } catch (err) {

                    console.error(err);
                }

            }, 1000);
        });
    }

    /* =========================
       STOP WEBCAM
    ========================= */

    if (stopBtn) {

        stopBtn.addEventListener("click", () => {

            webcamStream.src = "";

            if (poseInterval) {

                clearInterval(poseInterval);

                poseInterval = null;
            }

            poseText.innerText =
                "Stopped";

            confidenceText.innerText =
                "0%";

            recommendationText.innerText =
                "---";

            correctionText.innerText =
                "---";
        });
    }

    /* =========================
       SEND IMAGE
    ========================= */

    async function sendToBackend(formData) {

        uploadResult.style.display = "block";

        uploadPoseText.innerText =
            "Detecting...";

        uploadConfidenceText.innerText =
            "...";

        try {

            const res = await fetch(
                "http://127.0.0.1:5000/predict",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await res.json();

            if (data.error) {

                uploadPoseText.innerText =
                    data.error;

                uploadConfidenceText.innerText =
                    "0%";

            } else {

                uploadPoseText.innerText =
                    data.pose;

                uploadConfidenceText.innerText =
                    `${data.confidence}%`;
            }

        } catch (error) {

            console.error(error);

            uploadPoseText.innerText =
                "Server Error";

            uploadConfidenceText.innerText =
                "0%";
        }
    }

});