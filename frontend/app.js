const studentInput = document.querySelector("#student-id");
const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const refreshButton = document.querySelector("#refresh-state");
const errorBox = document.querySelector("#error");

const stateFields = {
  current_phase: document.querySelector("#state-phase"),
  current_lesson: document.querySelector("#state-lesson"),
  current_topic: document.querySelector("#state-topic"),
  current_mode: document.querySelector("#state-mode"),
  understanding_score: document.querySelector("#state-score"),
  next_step: document.querySelector("#state-next-step"),
};

function studentId() {
  return studentInput.value.trim() || "student_001";
}

function setBusy(isBusy) {
  sendButton.disabled = isBusy;
  refreshButton.disabled = isBusy;
  messageInput.disabled = isBusy;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function clearError() {
  errorBox.textContent = "";
  errorBox.hidden = true;
}

function appendMessage(role, text) {
  const item = document.createElement("div");
  item.className = `message ${role}`;
  item.textContent = text;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

function updateStatePanel(state) {
  stateFields.current_phase.textContent = state.current_phase || "-";
  stateFields.current_lesson.textContent = state.current_lesson || "-";
  stateFields.current_topic.textContent = state.current_topic || "-";
  stateFields.current_mode.textContent = state.current_mode || "-";
  stateFields.understanding_score.textContent =
    state.understanding_score === null || state.understanding_score === undefined
      ? "-"
      : String(state.understanding_score);
  stateFields.next_step.textContent = state.next_step || "-";
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json();
}

async function loadState() {
  clearError();
  setBusy(true);
  try {
    const state = await requestJson(`/state/${encodeURIComponent(studentId())}`);
    updateStatePanel(state);
  } catch (error) {
    showError(error.message);
  } finally {
    setBusy(false);
  }
}

async function sendMessage(text) {
  appendMessage("learner", text);
  const loadingMessage = appendMessage("assistant loading", "Thinking...");
  clearError();
  setBusy(true);
  try {
    const result = await requestJson("/chat", {
      method: "POST",
      body: JSON.stringify({ student_id: studentId(), message: text }),
    });
    loadingMessage.className = "message assistant";
    loadingMessage.textContent = result.message;
    updateStatePanel(result.state);
  } catch (error) {
    loadingMessage.remove();
    showError(error.message);
  } finally {
    setBusy(false);
    messageInput.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    return;
  }
  messageInput.value = "";
  sendMessage(text);
});

refreshButton.addEventListener("click", loadState);
studentInput.addEventListener("change", loadState);

appendMessage("assistant", "Send a message to start the learning loop.");
loadState();
