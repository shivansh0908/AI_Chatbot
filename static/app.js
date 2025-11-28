/* ====== SEND QUERY FUNCTION ====== */
async function sendQuery() 
{
    const input = document.getElementById("query");
    const text = input.value.trim();
    if (!text) return;

    const chatbox = document.getElementById("chatbox");
    
    // Hide welcome message on first message
    const welcomeMsg = chatbox.querySelector(".welcome-message");
    if (welcomeMsg) {
        welcomeMsg.style.display = "none";
    }

    // Reset textarea height
    input.style.height = "auto";

    // Add user message
    const userMsg = document.createElement("div");
    userMsg.className = "chat-message user";
    userMsg.textContent = text;
    chatbox.appendChild(userMsg);
    
    input.value = "";

    // Typing indicator
    const typing = document.createElement("div");
    typing.className = "chat-message bot";
    typing.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
    chatbox.appendChild(typing);

    chatbox.scrollTop = chatbox.scrollHeight;

    try {
        const res = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: text })
        });

        if (!res.ok) throw new Error("Server error: " + res.status);

        const data = await res.json();

        typing.textContent = data.answer;
        chatbox.scrollTop = chatbox.scrollHeight;

    } catch (err) {
        typing.textContent = `Error: ${err.message}`;
    }
}


/* ====== SIDEBAR TOGGLE FUNCTION ====== */
function toggleSidebar() 
{
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("sidebar-open");
}


/* ====== WELCOME MESSAGES (NEW FEATURE) ====== */
const welcomeMessages = [
    "How may I help you?",
    "Let me know your queries.",
    "Always there for your assistance.",
    "What would you like to know?",
    "Always here for you."
];

let welcomeIndex = 0;


/* ====== CLEAR CHAT (NEW CHAT BUTTON) ====== */
function clearChat() 
{
    const chatbox = document.getElementById("chatbox");
    const input = document.getElementById("query");

    // Remove all chat messages
    chatbox.innerHTML = "";

    // Cycle to next welcome message
    welcomeIndex = (welcomeIndex + 1) % welcomeMessages.length;

    // Add the new welcome message
    const welcomeMsg = document.createElement("div");
    welcomeMsg.className = "welcome-message";
    welcomeMsg.innerHTML = `<h1 class="welcome-title">${welcomeMessages[welcomeIndex]}</h1>`;
    chatbox.appendChild(welcomeMsg);

    // Clear input and reset height
    input.value = "";
    input.style.height = "auto";

    // Close sidebar
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.remove("sidebar-open");
}
