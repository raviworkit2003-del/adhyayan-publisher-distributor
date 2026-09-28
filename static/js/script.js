// ======================================================
// Adhyayan Publisher & Distributor
// Main JavaScript File
// ======================================================

const img = document.querySelector(".about-img");

if (img) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                img.classList.add("show");
            }
        });
    });

    observer.observe(img);
}