const uploadIcon = document.getElementById("upload-icon");
const uploadTitle = document.getElementById("upload-title");
const uploadSubtitle = document.getElementById("upload-subtitle");
const uploadCard = document.getElementById("upload-card");
const fileInput = document.getElementById("report-upload");
const analyzeBtn = document.getElementById("analyze-btn");


uploadCard.addEventListener("click", function ()
{
    fileInput.click();
});


fileInput.addEventListener("change", function ()
{
    const file = fileInput.files[0];
    if (!file)
    {
        return;
    }
    uploadIcon.textContent = "📄";
    uploadTitle.textContent = file.name;
    uploadSubtitle.textContent = "Ready to Analyze";
    analyzeBtn.style.display = "inline-block";
});


analyzeBtn.addEventListener("click", function ()
{
    uploadFile();
});


function uploadFile()
{
    const file = fileInput.files[0];
    if (!file)
    {
        return;
    }

    const formData = new FormData();
    formData.append("report", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })

    .then(response => response.json())
    .then(data => {
        console.table(data);
    })

    .catch(error => {
        console.error(error);
    });

}