const uploadIcon = document.getElementById("upload-icon");
const uploadTitle = document.getElementById("upload-title");
const uploadSubtitle = document.getElementById("upload-subtitle");

const uploadSection = document.getElementById("upload-section");
const uploadCard = document.getElementById("upload-card");
const fileInput = document.getElementById("report-upload");
const analyzeBtn = document.getElementById("analyze-btn");

const navUploadBtn = document.getElementById("nav-upload-btn");
const heroUploadBtn = document.getElementById("hero-upload-btn");

function openFilePicker()
{
    fileInput.click();
}


uploadCard.addEventListener("click", function (event)
{
    if (event.target.tagName !== "BUTTON")
    {
        openFilePicker();
    }
});



navUploadBtn.addEventListener("click", function ()
{
    uploadSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
});


    
heroUploadBtn.addEventListener("click", function ()
{
    uploadSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
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

    analyzeBtn.hidden = false;

    uploadCard.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
});


document
    .getElementById("learn-more-btn")
    .addEventListener("click", () => {

        document
            .getElementById("features")
            .scrollIntoView({
                behavior: "smooth"
            });

    });