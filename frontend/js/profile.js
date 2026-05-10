document.getElementById("profileForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const user_id = localStorage.getItem("user_id");

    const inputs = document.querySelectorAll("#profileForm input, #profileForm select");

    const data = {
        user_id: user_id,
        full_name: inputs[0].value,
        age: inputs[1].value,
        gender: inputs[2].value,
        experience: inputs[3].value,
        goal: inputs[4].value,
        height: inputs[5].value,
        weight: inputs[6].value,
        injury: inputs[7].value
    };

    const res = await fetch("http://127.0.0.1:5000/save_profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await res.json();

    alert(result.message);

    // 👉 AFTER SAVE → GO TO MAIN PAGE
    window.location.href = "index.html";
});