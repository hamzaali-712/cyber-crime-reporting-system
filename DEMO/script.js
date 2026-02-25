document.addEventListener("DOMContentLoaded", function() {
    const loader = document.getElementById("loader-wrapper");

    // Function to handle redirection with animation
    function redirectWithAnimation(url) {
        if(loader) {
            loader.style.display = "flex"; // Animation show karein
            setTimeout(() => {
                window.location.href = url; // 2 seconds baad redirect karein
            }, 2000);
        } else {
            window.location.href = url; // Agar loader na ho to direct redirect
        }
    }

    // 1. Report crime as Guest
    const guestBtn = document.querySelector(".primary-btn:nth-child(1)");
    if(guestBtn) {
        guestBtn.onclick = function() {
            redirectWithAnimation("../Demo/complaint_form.html");
        };
    }

    // 2. Login as Anti-Crimes
    const antiBtn = document.querySelector(".primary-btn:nth-child(2)");
    if(antiBtn) {
        antiBtn.onclick = function() {
            redirectWithAnimation("../Demo/admin_login.html");
        };
    }

    const SuperadminBtn = document.querySelector(".primary-btn:nth-child(3)");
    if(SuperadminBtn) {
        SuperadminBtn.onclick = function() {
            redirectWithAnimation("../Demo/super_admin_login.html");
        };
    }
    

    // 4. Go to Website (Naya Button Logic)
    // Ye 4th button ko select karega jo aapne abhi HTML mein add kiya hai
    const websiteBtn = document.querySelector(".website-btn");
    if(websiteBtn) {
        websiteBtn.onclick = function() {
            // FrontEnd folder ke andar htmlarea.html par bhejega
            redirectWithAnimation("../FrontEnd/htmlarea.html");
        };
    }
});