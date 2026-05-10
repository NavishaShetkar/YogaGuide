const container = document.querySelector('.container');
const LoginLink = document.querySelector('.SignInLink');
const RegisterLink = document.querySelector('.SignUpLink');

// Switch forms
RegisterLink.addEventListener('click', () => {
    container.classList.add('active');
});
LoginLink.addEventListener('click', () => {
    container.classList.remove('active');
});

// SIGN UP
document.querySelector(".Register form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.querySelector(".Register input[type='text']").value;
    const email = document.querySelector(".Register input[type='email']").value;
    const password = document.querySelector(".Register input[type='password']").value;

    const res = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, email, password })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    console.log("Registered Successfully!");

    // 👉 GO TO PROFILE PAGE
    window.top.location.href = "profile.html";
});

// LOGIN
// LOGIN
document.querySelector(".Login form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.querySelector(".Login input[type='email']").value;
    const password = document.querySelector(".Login input[type='password']").value;

    const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    alert("Login Successful!");

    // ✅ STORE USER ID (only once)
    localStorage.setItem("user_id", data.user_id);

    // ✅ CHECK PROFILE
    const res2 = await fetch(`http://127.0.0.1:5000/check_profile/${data.user_id}`);
    const profileData = await res2.json();

    if (profileData.exists) {
        window.top.location.href = "index.html";
    } else {
        window.top.location.href = "profile.html";
    }
});