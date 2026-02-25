/**
 * Dashboard Management Logic
 * Handles Complaint deletion and Status Color changes
 */

// Function to delete a row with animation
function deleteComplaint(rowId) {
    if (confirm("Are you sure you want to permanently delete this record?")) {
        const row = document.getElementById(rowId);
        
        if (row) {
            row.style.transition = '0.3s';
            row.style.opacity = '0';
            row.style.transform = 'translateX(20px)';
            
            setTimeout(() => {
                row.remove();
                console.log(`Record ${rowId} removed from temporary session.`);
                // Note: Real database connection yahan total count update karegi
            }, 300);
        }
    }
}

// Function to change dropdown border color based on status
function changeStatusColor(select) {
    const val = select.value;
    
    // Status ke mutabiq colors set karna
    switch(val) {
        case 'completed':
            select.style.borderColor = '#00c851'; // Green
            select.style.boxShadow = '0 0 5px rgba(0, 200, 81, 0.2)';
            break;
        case 'incomplete':
            select.style.borderColor = '#ff4444'; // Red
            select.style.boxShadow = '0 0 5px rgba(255, 68, 68, 0.2)';
            break;
        case 'progress':
            select.style.borderColor = '#ffbb33'; // Orange/Yellow
            select.style.boxShadow = '0 0 5px rgba(255, 187, 51, 0.2)';
            break;
        default:
            select.style.borderColor = 'rgba(0, 210, 255, 0.15)';
    }
}

// Page load par saare dropdowns ka initial color set karne ke liye
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.status-select').forEach(select => {
        changeStatusColor(select);
    });
});