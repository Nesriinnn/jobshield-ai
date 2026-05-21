const API_URL = "http://127.0.0.1:8000/analyze";

const pages = document.querySelectorAll(".page");
const navLinks = document.querySelectorAll(".nav-link");
const pageTargetButtons = document.querySelectorAll("[data-page-target]");
const jobText = document.getElementById("jobText");
const charCounter = document.getElementById("charCounter");
const analyzeBtn = document.getElementById("analyzeBtn");
const errorMessage = document.getElementById("errorMessage");
const resultCard = document.getElementById("resultCard");
const riskBadge = document.getElementById("riskBadge");
const confidenceScore = document.getElementById("confidenceScore");
const verdictText = document.getElementById("verdictText");
const fraudScore = document.getElementById("fraudScore");
const aiExplanation = document.getElementById("aiExplanation");
const redFlagsList = document.getElementById("redFlagsList");
const totalChecks = document.getElementById("totalChecks");
const fraudCount = document.getElementById("fraudCount");
const avgRisk = document.getElementById("avgRisk");
const historyList = document.getElementById("historyList");

const analysisHistory = [];

function showPage(pageId) {
    pages.forEach((page) => page.classList.toggle("active", page.id === pageId));
    navLinks.forEach((link) => link.classList.toggle("active", link.dataset.page === pageId));
}

function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.classList.toggle("loading", isLoading);
    analyzeBtn.querySelector(".btn-label").textContent = isLoading ? "Analyzing" : "Analyze";
}

function friendlyError(error) {
    if (error.message.includes("Failed to fetch")) {
        return "Could not connect to the backend. Make sure FastAPI is running on http://127.0.0.1:8000.";
    }

    return error.message || "Something went wrong while analyzing this job post.";
}

function riskClass(level) {
    return {
        High: "risk-high",
        Medium: "risk-medium",
        Low: "risk-low",
    }[level] || "risk-low";
}

function renderResult(result) {
    resultCard.classList.remove("hidden");
    riskBadge.className = `risk-badge ${riskClass(result.risk_level)}`;
    riskBadge.textContent = `${result.risk_level} risk`;
    confidenceScore.textContent = `Confidence: ${result.confidence_score}%`;
    verdictText.textContent = result.verdict;
    fraudScore.textContent = result.fraud_score;
    aiExplanation.textContent = result.explanation;

    redFlagsList.innerHTML = "";
    const redFlags = result.red_flags.length ? result.red_flags : ["No obvious keyword red flags detected."];

    redFlags.forEach((flag) => {
        const item = document.createElement("li");
        item.textContent = flag;
        redFlagsList.appendChild(item);
    });
}

function updateDashboard() {
    totalChecks.textContent = analysisHistory.length;
    fraudCount.textContent = analysisHistory.filter((item) => item.verdict === "Fraudulent").length;

    const averageRisk = analysisHistory.length ?
        Math.round(analysisHistory.reduce((sum, item) => sum + item.fraud_score, 0) / analysisHistory.length) :
        0;
    avgRisk.textContent = `${averageRisk}%`;
}

function updateHistory() {
    historyList.innerHTML = "";

    if (!analysisHistory.length) {
        const empty = document.createElement("p");
        empty.textContent = "No analyses yet.";
        empty.className = "explanation";
        historyList.appendChild(empty);
        return;
    }

    analysisHistory.slice(0, 6).forEach((item) => {
        const row = document.createElement("article");
        row.className = "history-item";
        row.innerHTML = `
            <strong>${item.verdict} - ${item.fraud_score}% - ${item.risk_level} risk</strong>
            <p>${item.preview}</p>
        `;
        historyList.appendChild(row);
    });
}

async function analyzeJob() {
    const text = jobText.value.trim();
    errorMessage.textContent = "";

    if (text.length < 20) {
        errorMessage.textContent = "Please paste a longer job description before analyzing.";
        return;
    }

    setLoading(true);

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ job_text: text }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "The backend could not analyze this job post.");
        }

        renderResult(data);
        analysisHistory.unshift({
            ...data,
            preview: text.slice(0, 120) + (text.length > 120 ? "..." : ""),
        });
        updateDashboard();
        updateHistory();
    } catch (error) {
        errorMessage.textContent = friendlyError(error);
    } finally {
        setLoading(false);
    }
}

navLinks.forEach((link) => {
    link.addEventListener("click", () => showPage(link.dataset.page));
});

pageTargetButtons.forEach((button) => {
    button.addEventListener("click", () => showPage(button.dataset.pageTarget));
});

jobText.addEventListener("input", () => {
    charCounter.textContent = `${jobText.value.length} characters`;
});

analyzeBtn.addEventListener("click", analyzeJob);
updateHistory();