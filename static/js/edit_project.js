document.addEventListener("DOMContentLoaded", function () {

    const toast = document.querySelector('.toast');

    if (toast) {
        setTimeout(() => {
            toast.style.opacity = '0';
        }, 3000);
    }

});