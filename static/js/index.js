document.addEventListener("DOMContentLoaded", function () {

    // 🔹 SCROLL HELPER
    function scrollWithOffset(element) {
        if (!element) return;

        const navbar = document.querySelector(".navbar");
        const navbarHeight = navbar ? navbar.offsetHeight : 80;

        const y = element.offsetTop - navbarHeight - 10;

        window.scrollTo({
            top: y,
            behavior: "smooth"
        });
    }

    // 🔹 EXPERIENCE
    window.showExperience = function(event) {
        if (event) event.preventDefault();

        const section = document.getElementById("experience");
        scrollWithOffset(section);
    };

    // 🔹 EDUCATION (🔥 FIXED)
    window.showEducation = function(event) {
        if (event) event.preventDefault();

        const section = document.getElementById("education");
        scrollWithOffset(section);
    };

    // 🔹 PROJECTS
    window.showProjects = function(event) {
        if (event) event.preventDefault();

        const section = document.getElementById("projects-section");
        scrollWithOffset(section);
    };

    // 🔹 CERTIFICATES
    window.showCertificates = function(event) {
        if (event) event.preventDefault();

        const section = document.getElementById("certificates-section");
        scrollWithOffset(section);
    };

    // 🔹 HOME
    window.goHome = function(event) {
        if (event) event.preventDefault();

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };

    // 🔹 FLASH AUTO HIDE
    setTimeout(() => {
        const flash = document.querySelector('.flash-container');
        if (flash) {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }
    }, 2000);

    // 🔹 THEME TOGGLE
    const toggleBtn = document.getElementById("themeToggle");

    if (toggleBtn) {
        if (localStorage.getItem("theme") === "light") {
            document.body.classList.add("light-theme");
            toggleBtn.textContent = "☀️";
        }

        toggleBtn.addEventListener("click", () => {
            document.body.classList.toggle("light-theme");

            if (document.body.classList.contains("light-theme")) {
                localStorage.setItem("theme", "light");
                toggleBtn.textContent = "☀️";
            } else {
                localStorage.setItem("theme", "dark");
                toggleBtn.textContent = "🌙";
            }
        });
    }

    // 🔹 DOWNLOAD RESUME
    window.downloadResume = function(e) {
        e.preventDefault();

        const link = document.createElement('a');
        link.href = "/static/files/Darshan_Resume.pdf";
        link.download = "Darshan_Resume.pdf";
        link.click();
    };

});