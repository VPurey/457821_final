const API_BASE_URL = "http://127.0.0.1:8000";

// DOM Elements
const githubTokenInput = document.getElementById("github-token");
const openaiKeyInput = document.getElementById("openai-key");
const btnLoadRepos = document.getElementById("btn-load-repos");
const repoSelect = document.getElementById("repo-select");
const chatWindow = document.getElementById("chat-window");
const userQuestion = document.getElementById("user-question");
const btnSend = document.getElementById("btn-send");
const authError = document.getElementById("auth-error");
const chatError = document.getElementById("chat-error");

// 1. Fetch Repositories from Backend
btnLoadRepos.addEventListener("click", async () => {
  const token = githubTokenInput.value.trim();

  if (!token) {
    authError.textContent = "Please enter a valid GitHub token.";
    return;
  }

  authError.textContent = "";
  btnLoadRepos.disabled = true;
  btnLoadRepos.textContent = "Connecting...";

  try {
    const response = await fetch(`${API_BASE_URL}/api/repositories`, {
      method: "GET",
      headers: {
        "X-GitHub-Token": token,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to fetch repositories.");
    }

    // Populate the dropdown list
    repoSelect.innerHTML =
      '<option value="">-- Choose a Repository --</option>';
    data.repositories.forEach((repo) => {
      const option = document.createElement("option");
      // Extract the .name string from the mock object
      option.value = repo.full_name;
      option.textContent = repo.name;
      repoSelect.appendChild(option);
    });

    // Enable UI elements upon success
    repoSelect.disabled = false;
    userQuestion.disabled = false;
    btnSend.disabled = false;
  } catch (error) {
    authError.textContent = error.message;
    repoSelect.disabled = true;
    repoSelect.innerHTML =
      '<option value="">-- Connect GitHub first --</option>';
  } finally {
    btnLoadRepos.disabled = false;
    btnLoadRepos.textContent = "Connect & Load Repositories";
  }
});

// 2. Stream/Post Question to AI
btnSend.addEventListener("click", async () => {
  const token = githubTokenInput.value.trim();
  const openaiKey = openaiKeyInput.value.trim();
  // Correctly assigned using 'const' and targeting our DOM element 'repoSelect'
  const repoName = repoSelect.value;
  const question = userQuestion.value.trim();

  if (!token || !openaiKey || !repoName || !question) {
    chatError.textContent =
      "Ensure all tokens are filled, a repo is selected, and your question is not empty.";
    return;
  }

  chatError.textContent = "";
  btnSend.disabled = true;
  btnSend.textContent = "Analyzing...";

  // Append the user message visually to the chat window
  appendMessage(question, "user-msg");
  userQuestion.value = "";

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-GitHub-Token": token,
      },
      body: JSON.stringify({
        repo_name: repoName,
        question: question,
        openai_key: openaiKey,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Error processing your chat request.");
    }

    // Append the AI reply
    appendMessage(data.response, "ai-msg");
  } catch (error) {
    chatError.textContent = error.message;
    appendMessage(`Error: ${error.message}`, "ai-msg");
  } finally {
    btnSend.disabled = false;
    btnSend.textContent = "Ask AI";
  }
});

// Helper function to append elements to chat log
function appendMessage(text, className) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `msg ${className}`;
  msgDiv.textContent = text;
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll to the bottom
}

document.addEventListener("DOMContentLoaded", () => {
  const themeToggleBtn = document.getElementById("theme-toggle");

  // Check localStorage for previous preference, otherwise default to dark mode
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-mode");
  }

  themeToggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");

    // Save choice
    if (document.body.classList.contains("light-mode")) {
      localStorage.setItem("theme", "light");
    } else {
      localStorage.setItem("theme", "dark");
    }
  });
});
