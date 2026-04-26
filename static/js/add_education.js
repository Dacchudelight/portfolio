window.onload = function () {
    const toasts = document.querySelectorAll('.toast');

    if (toasts.length === 0) return;

    setTimeout(() => {
        toasts.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateX(20px)';

            setTimeout(() => {
                el.remove();
            }, 300);
        });
    }, 2000); // 2 seconds
};
