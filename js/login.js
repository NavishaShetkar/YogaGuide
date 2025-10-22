const container = document.querySelector('.container');
const LoginLink = document.querySelector('.SignInLink');
const RegisterLink = document.querySelector('.SignUpLink');

// Get the forms (IDs added in login.html and signup.html)
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

// Logic for switching between login/register views
RegisterLink.addEventListener('click', () =>{
    container.classList.add('active');
})

LoginLink.addEventListener('click', () => {
    container.classList.remove('active');
})

// NEW: Logic for handling successful Register and redirecting
if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        // Simulate a successful registration
        alert("Registration Successful! Please log in.");
        
        // Check if the user is on the separate signup.html page (redirect to login)
        if (window.location.pathname.endsWith('signup.html')) {
            window.location.href = 'login.html';
        } else {
            // If user registered from within the login.html, just switch to login view
            container.classList.remove('active');
        }
    });
}

// NEW: Logic for handling successful Login and redirecting to the main app
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        // Simulate a successful login
        alert("Login Successful! Redirecting to Yoga Pose Detection...");
        // Redirect to the main application page
        window.location.href = 'index.html';
    });
}