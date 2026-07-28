window.addEventListener("scroll", function(){
    const navbar = document.querySelector(".navbar");
    if(window.scrollY > 20){

        navbar.classList.add("scrolled");
    }
    else{

        navbar.classList.remove("scrolled");
    }
});

const uploadCard = document.getElementById("upload-card");
const fileInput = document.getElementById("report-upload");
const uploadIcon = document.getElementById("upload-icon");
const uploadTitle = document.getElementById("upload-title");
const uploadDivider = document.getElementById("upload-divider");
const uploadSubtitle = document.getElementById("upload-subtitle");
const uploadInfo = document.getElementById("upload-info");
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

    if (file.type !== "application/pdf")
    {

        alert("Please upload a PDF.");
        fileInput.value = "";
        return;
    }

    if (file.size > 10 * 1024 * 1024)
    {

        alert("Maximum file size is 10 MB.");
        fileInput.value = "";
        return;
    }

    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    uploadIcon.textContent = "📄";
    uploadTitle.textContent = file.name;
    uploadDivider.style.display = "none";
    uploadSubtitle.textContent = `${sizeMB} MB • ✓ Ready to Analyze`;
    analyzeBtn.hidden = false;
});