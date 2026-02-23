function goToReport() {
  document.getElementById("login-page").classList.remove("active");
  document.getElementById("report-page").classList.add("active");
}

document.getElementById("crimeForm").addEventListener("submit", function(e) {
  e.preventDefault();
  const files = document.getElementById("fileUpload").files;
  let totalSize = 0;
  for (let i = 0; i < files.length; i++) {
    totalSize += files[i].size;
  }
  if (totalSize > 500 * 1024 * 1024) {
    alert("File size exceeds 500MB limit!");
    return;
  }
  alert("Report submitted successfully!");
  this.reset();
});
