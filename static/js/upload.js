const uploadIcon = document.getElementById("upload-icon");
const uploadTitle = document.getElementById("upload-title");
const uploadSubtitle = document.getElementById("upload-subtitle");

const uploadCard = document.getElementById("upload-card");
const fileInput = document.getElementById("report-upload");

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

});