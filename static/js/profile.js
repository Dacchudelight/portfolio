// 🔥 AUTO HIDE TOAST
document.addEventListener("DOMContentLoaded", function () {
    const toast = document.getElementById("toast");

    if (toast) {
        // show animation already applied via class
        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }
});


// 🔥 OPTIONAL: SMOOTH INPUT FOCUS EFFECT (nice UX)
const inputs = document.querySelectorAll("input, textarea");

inputs.forEach(input => {
    input.addEventListener("focus", () => {
        input.style.border = "1px solid #22c55e";
    });

    input.addEventListener("blur", () => {
        input.style.border = "none";
    });
});