document.addEventListener("DOMContentLoaded", function () {

    // 🔥 AUTO HIDE TOAST
    const toast = document.getElementById("toast");

    if (toast) {
        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }

    // 🔥 INPUT FOCUS EFFECT (SAFE)
    const inputs = document.querySelectorAll("input, textarea");

    inputs.forEach(input => {
        input.addEventListener("focus", () => {
            input.style.borderColor = "#22c55e";
        });

        input.addEventListener("blur", () => {
            input.style.borderColor = "";
        });
    });

});