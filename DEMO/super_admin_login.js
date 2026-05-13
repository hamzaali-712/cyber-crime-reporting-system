document.getElementById('superLoginForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Form refresh hone se rokne ke liye

    // Inputs se values lena
    const user = document.getElementById('superUser').value;
    const pass = document.getElementById('superPass').value;

    // Credentials Check
    if (user === "admin" && pass === "1234") {
        // Success: Redirect to Super Admin Dashboard
        alert("Verification Successful! Accessing Master Controls...");
        window.location.href = "super_admin_dashboard.html";
    } else {
        // Failure: Error message
        alert("Access Denied: Invalid Username or Password.");

        // Input fields clear karna
        document.getElementById('superPass').value = "";
    }
});