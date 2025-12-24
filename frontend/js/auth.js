//Signup API Call
// ---------------- REGISTER ----------------
function registerUser() {
    const username = document.getElementById("reg-username").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    fetch("http://127.0.0.1:5000/register", {   // FIXED
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, email, password })
    })
    .then(async (res) => {
        const data = await res.json();
        alert(data.message || data.error);

        if (res.status === 201) {
            // switch to login form
            document.querySelector(".container").classList.remove("active");
        }
    });
}


// ---------------- LOGIN ----------------
function loginUser() {
    const email = document.getElementById("login-username").value;  // FIXED
    const password = document.getElementById("login-password").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password })   // FIXED
    })
    .then(async (res) => {
        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        if (res.status === 200) {
            alert("Login successful!");
            localStorage.setItem("user", email);
            window.location.href = "index.html";  // redirect to your dashboard
        }
    });
}
