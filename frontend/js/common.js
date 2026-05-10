function openLogin() {
    const modal = document.getElementById("loginModal");
    const container = document.getElementById("loginContainer");

    modal.style.display = "flex";

    fetch("login.html")
        .then(res => res.text())
        .then(html => {
            container.innerHTML = html;

            // Load login.js AFTER login.html is loaded
            const script = document.createElement("script");
            script.src = "js/login.js";
            container.appendChild(script);
        })
        .catch(err => console.error("Error loading login.html:", err));
}

function closeLogin() {
    document.getElementById("loginModal").style.display = "none";
}

