// Smooth scroll effect
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e){
        e.preventDefault();
    });
});

// Navbar shadow on scroll
window.addEventListener("scroll", function(){
    const header = document.querySelector("header");
    header.style.boxShadow = window.scrollY > 20 ? 
        "0 4px 10px rgba(0,0,0,0.5)" : "none";
});