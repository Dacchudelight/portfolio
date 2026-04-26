document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================
       PARTICLE CANVAS — HERO BACKGROUND
       ========================================== */
    const canvas = document.getElementById("particleCanvas");
    if (canvas) {
        const ctx = canvas.getContext("2d");
        let particles = [];
        let mouse = { x: null, y: null };

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        resizeCanvas();
        window.addEventListener("resize", resizeCanvas);

        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        });
        canvas.addEventListener("mouseleave", () => { mouse.x = null; mouse.y = null; });

        class Particle {
            constructor() { this.reset(); }
            reset() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 2 + 0.5;
                this.speedX = (Math.random() - 0.5) * 0.4;
                this.speedY = (Math.random() - 0.5) * 0.4;
                this.opacity = Math.random() * 0.5 + 0.1;
            }
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
                if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
                if (mouse.x !== null) {
                    const dx = mouse.x - this.x, dy = mouse.y - this.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        this.x -= dx * 0.01;
                        this.y -= dy * 0.01;
                    }
                }
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(139, 92, 246, ${this.opacity})`;
                ctx.fill();
            }
        }

        function initParticles() {
            particles = [];
            const count = Math.min(Math.floor((canvas.width * canvas.height) / 12000), 80);
            for (let i = 0; i < count; i++) particles.push(new Particle());
        }
        initParticles();

        function drawConnections() {
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 150) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(139, 92, 246, ${0.08 * (1 - dist / 150)})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
        }

        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => { p.update(); p.draw(); });
            drawConnections();
            requestAnimationFrame(animateParticles);
        }
        animateParticles();
        window.addEventListener("resize", initParticles);
    }

    /* ==========================================
       SCROLL REVEAL — INTERSECTION OBSERVER
       ========================================== */
    const revealElements = document.querySelectorAll("[data-reveal]");
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add("revealed");
                }, index * 80);
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });
    revealElements.forEach(el => revealObserver.observe(el));

    /* ==========================================
       TYPING EFFECT
       ========================================== */
    const typewriterEl = document.getElementById("typewriter");
    if (typewriterEl) {
        const fullText = typewriterEl.textContent.trim();
        typewriterEl.textContent = "";
        let charIndex = 0;
        function typeChar() {
            if (charIndex < fullText.length) {
                typewriterEl.textContent += fullText.charAt(charIndex);
                charIndex++;
                setTimeout(typeChar, 70);
            }
        }
        setTimeout(typeChar, 800);
    }

    /* ==========================================
       NAVBAR SCROLL EFFECT
       ========================================== */
    const navbar = document.getElementById("mainNav");
    let lastScroll = 0;
    window.addEventListener("scroll", () => {
        const currentScroll = window.scrollY;
        if (navbar) {
            if (currentScroll > 50) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        }
        lastScroll = currentScroll;
    });

    /* ==========================================
       ACTIVE NAV LINK TRACKING
       ========================================== */
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                navLinks.forEach(link => link.classList.remove("active"));
                const matchingLink = document.querySelector(`.nav-link[onclick*="${id}"]`);
                if (matchingLink) matchingLink.classList.add("active");
            }
        });
    }, { threshold: 0.3, rootMargin: "-100px 0px -50% 0px" });
    sections.forEach(s => sectionObserver.observe(s));

    /* ==========================================
       HAMBURGER MENU
       ========================================== */
    const hamburger = document.getElementById("hamburgerBtn");
    const navLinksContainer = document.getElementById("navLinks");
    if (hamburger && navLinksContainer) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("active");
            navLinksContainer.classList.toggle("mobile-open");
        });
        navLinksContainer.querySelectorAll("a").forEach(link => {
            link.addEventListener("click", () => {
                hamburger.classList.remove("active");
                navLinksContainer.classList.remove("mobile-open");
            });
        });
    }

    /* ==========================================
       SCROLL HELPER
       ========================================== */
    function scrollWithOffset(element) {
        if (!element) return;
        const navbarEl = document.querySelector(".navbar");
        const navbarHeight = navbarEl ? navbarEl.offsetHeight : 80;
        const y = element.offsetTop - navbarHeight - 20;
        window.scrollTo({ top: y, behavior: "smooth" });
    }

    /* ==========================================
       NAVIGATION FUNCTIONS
       ========================================== */
    window.showExperience = function(event) {
        if (event) event.preventDefault();
        scrollWithOffset(document.getElementById("experience"));
    };

    window.showEducation = function(event) {
        if (event) event.preventDefault();
        scrollWithOffset(document.getElementById("education"));
    };

    window.showProjects = function(event) {
        if (event) event.preventDefault();
        scrollWithOffset(document.getElementById("projects-section"));
    };

    window.showCertificates = function(event) {
        if (event) event.preventDefault();
        scrollWithOffset(document.getElementById("certificates-section"));
    };

    window.showContact = function(event) {
        if (event) event.preventDefault();
        scrollWithOffset(document.getElementById("contact"));
    };

    window.goHome = function(event) {
        if (event) event.preventDefault();
        window.scrollTo({ top: 0, behavior: "smooth" });
        navLinks.forEach(l => l.classList.remove("active"));
        const homeLink = document.querySelector('.nav-link[onclick*="goHome"]');
        if (homeLink) homeLink.classList.add("active");
    };

    /* ==========================================
       FLASH AUTO HIDE
       ========================================== */
    setTimeout(() => {
        const flash = document.querySelector('.flash-container');
        if (flash) {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(40px)';
            setTimeout(() => flash.remove(), 500);
        }
    }, 3000);

    /* ==========================================
       THEME TOGGLE
       ========================================== */
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

    /* ==========================================
       DOWNLOAD RESUME
       ========================================== */
    window.downloadResume = function(e) {
        e.preventDefault();
        const link = document.createElement('a');
        link.href = "/static/files/Darshan_Resume.pdf";
        link.download = "Darshan_Resume.pdf";
        link.click();
    };

    /* ==========================================
       PROJECT CARD TILT EFFECT
       ========================================== */
    document.querySelectorAll('.project-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });

});