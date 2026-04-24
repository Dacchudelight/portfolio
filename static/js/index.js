function showProjects(event) {
    if (event) event.preventDefault();

    const proj = document.getElementById("projects-section");
    const btnProj = document.getElementById("btn-projects");

    proj.classList.remove("hidden-section");
    proj.classList.add("show-section");

    btnProj.classList.add("active-btn");

    window.scrollTo({ top: proj.offsetTop - 80, behavior: 'smooth' });
}

function showCertificates(event) {
    if (event) event.preventDefault();

    const cert = document.getElementById("certificates-section");
    const btnCert = document.getElementById("btn-certificates");

    cert.classList.remove("hidden-section");
    cert.classList.add("show-section");

    btnCert.classList.add("active-btn");

    window.scrollTo({ top: cert.offsetTop - 80, behavior: 'smooth' });
}

function goHome(event) {
    if (event) event.preventDefault();

    const proj = document.getElementById("projects-section");
    const cert = document.getElementById("certificates-section");

    proj.classList.add("hidden-section");
    cert.classList.add("hidden-section");

    proj.classList.remove("show-section");
    cert.classList.remove("show-section");

    window.scrollTo({ top: 0, behavior: 'smooth' });
}
    setTimeout(() => {
        const flash = document.querySelector('.flash-container');
        if (flash) {
            flash.style.opacity = '0';
            setTimeout(() => {
                flash.remove();
            }, 500); // smooth fade out
        }
    }, 2000); // 2 seconds
    
    
    //LIGHT THEME
const toggleBtn = document.getElementById("themeToggle");

// Load saved theme
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




function downloadResume(e) {
    e.preventDefault();

    const link = document.createElement('a');
    link.href = "{{ url_for('static', filename='files/Darshan_Resume.pdf') }}";
    link.download = "Darshan_Resume.pdf";
    link.click();
}


const eduLink = document.getElementById("eduLink");
const eduSection = document.getElementById("education");

eduLink.addEventListener("click", function(e) {
    e.preventDefault();

    // Show section
    eduSection.style.display = "block";

    // Smooth scroll
    eduSection.scrollIntoView({
        behavior: "smooth"
    });
});
