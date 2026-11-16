// State management
let state = {
  messages: [],
  queryCount: 0,
  apiConnected: false,
};

// DOM Elements
const messagesContainer = document.getElementById('messages-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const statusBadge = document.getElementById('status-badge');
const statusText = document.getElementById('status-text');
const retryBtn = document.getElementById('retry-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');
const statQueries = document.getElementById('stat-queries');
const statMessages = document.getElementById('stat-messages');
const topKSlider = document.getElementById('top-k');
const topKVal = document.getElementById('top-k-val');
const thresholdSlider = document.getElementById('score-threshold');
const thresholdVal = document.getElementById('threshold-val');
const fallbackCheckbox = document.getElementById('llm-fallback');
const welcomeCard = document.getElementById('welcome-card');

// Update slider value displays
topKSlider.addEventListener('input', (e) => {
  topKVal.textContent = e.target.value;
});

thresholdSlider.addEventListener('input', (e) => {
  thresholdVal.textContent = parseFloat(e.target.value).toFixed(2);
});

// Check API Health
async function checkHealth() {
  statusBadge.className = 'badge badge-checking';
  statusText.textContent = 'Checking API...';

  try {
    const res = await fetch('/api/health');
    if (res.ok) {
      const data = await res.json();
      state.apiConnected = true;
      statusBadge.className = 'badge badge-connected';
      statusText.textContent = `${data.llm_provider || 'Connected'}`;
      return;
    }
  } catch (err) {
    console.warn('API health check error:', err);
  }

  // Fallback to /api/v1/health
  try {
    const res2 = await fetch('/api/v1/health');
    if (res2.ok) {
      const data2 = await res2.json();
      state.apiConnected = true;
      statusBadge.className = 'badge badge-connected';
      statusText.textContent = `${data2.llm_provider || 'Connected'}`;
      return;
    }
  } catch (e) {
    console.warn('v1 health error:', e);
  }

  state.apiConnected = false;
  statusBadge.className = 'badge badge-disconnected';
  statusText.textContent = 'Disconnected';
}

retryBtn.addEventListener('click', checkHealth);

// Format Timestamp
function getTimestamp() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Update Stats UI
function updateStats() {
  statQueries.textContent = state.queryCount;
  statMessages.textContent = state.messages.length;
}

// Append a message bubble to chat
function appendMessage(role, text, sources = [], matchesCount = 0) {
  if (welcomeCard && welcomeCard.parentElement) {
    // Hide welcome card after first message
    welcomeCard.style.display = 'none';
  }

  const time = getTimestamp();
  const bubble = document.createElement('div');
  bubble.className = `message-bubble ${role === 'user' ? 'user-message' : 'assistant-message'}`;

  const header = document.createElement('div');
  header.className = 'message-header';
  header.innerHTML = `
    <span>${role === 'user' ? '👤 You' : '🤖 Assistant'}</span>
    <span>${time}</span>
  `;

  const content = document.createElement('div');
  content.className = 'message-text';
  content.textContent = text;

  bubble.appendChild(header);
  bubble.appendChild(content);

  // Sources if available
  if (sources && sources.length > 0) {
    const sourcesBox = document.createElement('div');
    sourcesBox.className = 'sources-box';
    sourcesBox.innerHTML = `<strong>📑 Sources (${matchesCount} matches):</strong><br/>` +
      sources.map((s) => `<span>📄 ${escapeHtml(s)}</span>`).join('');
    bubble.appendChild(sourcesBox);
  }

  messagesContainer.appendChild(bubble);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  state.messages.push({ role, text, time });
  updateStats();
}

// Show typing indicator
function showTypingIndicator() {
  const indicator = document.createElement('div');
  indicator.id = 'typing-indicator';
  indicator.className = 'message-bubble assistant-message typing-indicator';
  indicator.innerHTML = `
    <span></span>
    <span></span>
    <span></span>
  `;
  messagesContainer.appendChild(indicator);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  return indicator;
}

function removeTypingIndicator() {
  const indicator = document.getElementById('typing-indicator');
  if (indicator) {
    indicator.remove();
  }
}

// Escape HTML utility
function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

// Send Question
async function handleSend(queryText) {
  const query = queryText.trim();
  if (!query) return;

  userInput.value = '';
  userInput.focus();

  appendMessage('user', query);
  state.queryCount++;
  updateStats();

  sendBtn.disabled = true;
  showTypingIndicator();

  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        top_k: parseInt(topKSlider.value, 10),
        score_threshold: parseFloat(thresholdSlider.value),
        fallback_to_llm: fallbackCheckbox.checked,
      }),
    });

    removeTypingIndicator();

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      appendMessage(
        'assistant',
        `❌ Error (${response.status}): ${errData.detail || response.statusText || 'Failed to get response from server.'}`
      );
      return;
    }

    const data = await response.json();
    appendMessage(
      'assistant',
      data.answer || 'No answer returned.',
      data.sources || [],
      data.matches_count || 0
    );
  } catch (err) {
    removeTypingIndicator();
    console.error('Query error:', err);
    appendMessage(
      'assistant',
      '⚠️ Connection Error: Unable to reach the backend API. Please make sure the service is running and properly configured.'
    );
  } finally {
    sendBtn.disabled = false;
  }
}

// Form submit
chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  handleSend(userInput.value);
});

// Clickable suggestion pills
document.querySelectorAll('.pill-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const query = btn.getAttribute('data-query');
    handleSend(query);
  });
});

// Clear Chat
clearChatBtn.addEventListener('click', () => {
  state.messages = [];
  state.queryCount = 0;
  messagesContainer.innerHTML = '';
  if (welcomeCard) {
    welcomeCard.style.display = 'block';
    messagesContainer.appendChild(welcomeCard);
  }
  updateStats();
});

// Initial startup health check
checkHealth();
