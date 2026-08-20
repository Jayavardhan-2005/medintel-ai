document.addEventListener("DOMContentLoaded", () => {

    const cards = document.querySelectorAll(".result-card");

    const modal = document.getElementById("parameter-modal");
    const modalOverlay = document.querySelector(".modal-overlay");
    const modalClose = document.getElementById("modal-close");

    const modalTitle = document.getElementById("modal-title");
    const modalStatus = document.getElementById("modal-status");

    const modalValue = document.getElementById("modal-value");
    const modalUnit = document.getElementById("modal-unit");

    const modalDescription = document.getElementById("modal-description");
    const modalRange = document.getElementById("modal-range");

    const modalLow = document.getElementById("modal-low");
    const modalHigh = document.getElementById("modal-high");

    const modalWhyTested = document.getElementById("modal-why-tested");

    const aiExplanation = document.getElementById("ai-explanation");

    async function openModal(card) {

        const test = card.dataset.test;
        const value = card.dataset.value;
        const unit = card.dataset.unit;
        const status = card.dataset.status;
        modalTitle.textContent = test;

        modalValue.textContent = value;
        modalUnit.textContent = unit;

        modalStatus.textContent = status;

        modalStatus.className =
            `status-badge ${status.toLowerCase()}`;

        modalDescription.textContent = "Loading...";
        modalRange.textContent = "Loading...";

        modalWhyTested.textContent = "Loading...";

        modalLow.innerHTML = "<li>Loading...</li>";
        modalHigh.innerHTML = "<li>Loading...</li>";

        aiExplanation.innerHTML =
            "<p>Loading explanation...</p>";
        modal.classList.add("active");
        modal.setAttribute("aria-hidden", "false");

        document.body.style.overflow = "hidden";
        try {

            const response = await fetch(
                `/test-knowledge/${encodeURIComponent(test)}`
            );

            if (!response.ok) {
                throw new Error("Knowledge request failed");
            }

            const data = await response.json();

            const knowledge = data.knowledge || data;

            modalDescription.textContent =
                knowledge.description ||
                "Information is not available.";

            modalRange.textContent =
                knowledge.reference_range ||
                "Reference range depends on the laboratory.";

            modalLow.innerHTML = "";

            if (
                Array.isArray(knowledge.low) &&
                knowledge.low.length > 0
            ) {

                knowledge.low.forEach(reason => {

                    const li = document.createElement("li");

                    li.textContent = reason;

                    modalLow.appendChild(li);

                });

            } else {

                modalLow.innerHTML =
                    "<li>Information is not available.</li>";

            }

            modalHigh.innerHTML = "";

            if (
                Array.isArray(knowledge.high) &&
                knowledge.high.length > 0
            ) {

                knowledge.high.forEach(reason => {

                    const li = document.createElement("li");

                    li.textContent = reason;

                    modalHigh.appendChild(li);

                });

            } else {

                modalHigh.innerHTML =
                    "<li>Information is not available.</li>";

            }

            modalWhyTested.textContent =
                knowledge.why_tested ||
                "Information is not available.";


        } catch (error) {

            console.error(
                "Knowledge loading error:",
                error
            );

            modalDescription.textContent =
                "Unable to load parameter information.";

            modalRange.textContent =
                "Information unavailable.";

            modalWhyTested.textContent =
                "Information unavailable.";

            modalLow.innerHTML =
                "<li>Information unavailable.</li>";

            modalHigh.innerHTML =
                "<li>Information unavailable.</li>";

        }
        try {

            const response = await fetch("/explain", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    test: test,
                    value: value,
                    unit: unit,
                    status: status

                })

            });


            if (!response.ok) {
                throw new Error(
                    "Explanation request failed"
                );
            }


            const data = await response.json();


            if (data.ai_explanation) {

    aiExplanation.innerHTML =
        `<p>${escapeHtml(data.ai_explanation)}</p>`;

} else if (data.knowledge) {

    aiExplanation.innerHTML =
        `<p>${escapeHtml(
            data.knowledge.guidance || ""
        )}</p>`;

} else {

    aiExplanation.innerHTML =
        "<p>Explanation unavailable.</p>";

}


        } catch (error) {

            console.error(
                "AI explanation error:",
                error
            );

            aiExplanation.innerHTML = `
                <p>
                    AI explanation is currently unavailable.
                    The information above is still available
                    from the medical knowledge base.
                </p>
            `;

        }

    }

    function closeModal() {

        modal.classList.remove("active");

        modal.setAttribute("aria-hidden", "true");

        document.body.style.overflow = "";

    }

    cards.forEach(card => {

        card.addEventListener("click", () => {

            openModal(card);

        });

        card.addEventListener("keydown", event => {

            if (
                event.key === "Enter" ||
                event.key === " "
            ) {

                event.preventDefault();

                openModal(card);

            }

        });

    });

    modalClose.addEventListener(
        "click",
        closeModal
    );


    modalOverlay.addEventListener(
        "click",
        closeModal
    );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape" &&
                modal.classList.contains("active")
            ) {

                closeModal();

            }

        }
    );

    function escapeHtml(text) {

        const div = document.createElement("div");

        div.textContent = text;

        return div.innerHTML;

    }

});