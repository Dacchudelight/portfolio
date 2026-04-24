document.addEventListener("DOMContentLoaded", function () {

    const toast = document.querySelector('.toast');

    if (toast) {
        setTimeout(() => {
            toast.style.opacity = '0';

            setTimeout(() => {
                toast.remove(); // ✅ completely removes from DOM
            }, 300);
        }, 3000);
    }

});