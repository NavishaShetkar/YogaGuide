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

    alert("Registered Successfully!");
    container.classList.remove("active");
});

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
    window.top.location.href = "index.html"
});
