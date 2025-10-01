let isConnected = false;
let currentStatus = {};
let connectionAttempts = 0;
let isRunning = false;
let connectionCheckInterval;
let websocket = null;
let reconnectTimeout = null;

function showNotification(message, type = "info") {
    console.log(`🔔 [${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-lg z-50 transition-all duration-300 ${
        type === 'error' ? 'bg-red-500 text-white' : 
        type === 'success' ? 'bg-green-500 text-white' : 
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// WebSocket connection
function connectWebSocket() {
    if (websocket) {
        websocket.close();
    }
    
    websocket = new WebSocket('ws://localhost:8081');
    
    websocket.onopen = function(event) {
        console.log('🔌 WebSocket connected');
        showNotification('✅ Real-time connection established', 'success');
        document.getElementById('connectionDot').className = 'w-3 h-3 bg-green-500 rounded-full pulse-glow';
        document.getElementById('connectionText').textContent = 'Real-time Connection Active';
        document.getElementById('connectionText').className = 'text-green-300 font-semibold';
    };
    
    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'status') {
            currentStatus = data.data;
            updateUI();
        }
    };
    
    websocket.onclose = function(event) {
        console.log('🔌 WebSocket disconnected');
        if (isConnected) {
            showNotification('⚠️ Real-time connection lost, switching to polling', 'error');
            startPolling();
        }
        // Attempt reconnect after 2 seconds
        reconnectTimeout = setTimeout(connectWebSocket, 2000);
    };
    
    websocket.onerror = function(error) {
        console.error('❌ WebSocket error:', error);
        if (!isConnected) {
            startPolling();
        }
    };
}

function startPolling() {
    console.log('🔄 Starting polling fallback');
    if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
    }
    connectionCheckInterval = setInterval(checkBackendConnection, 500);
}

async function checkBackendConnection() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1000);
        
        const res = await fetch("http://localhost:8080/status.json?" + Date.now(), {
            signal: controller.signal,
            cache: 'no-store'
        });
        
        clearTimeout(timeoutId);
        
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const newStatus = await res.json();
        currentStatus = newStatus;
        connectionAttempts = 0;
        
        if (!isConnected) {
            isConnected = true;
            showConnectedUI();
            showNotification("✅ Connected to Auto Clicker backend", "success");
        }
        
        updateUI();
        
    } catch (err) {
        connectionAttempts++;
        
        if (isConnected || connectionAttempts === 1) {
            console.warn("❌ Backend connection failed:", err.message);
        }
        
        if (isConnected) {
            isConnected = false;
            showDisconnectedUI();
            if (connectionAttempts > 1) {
                showNotification("❌ Lost connection to backend", "error");
            }
        }
        
        // Show download section if not connected
        document.getElementById('downloadSection').classList.remove('hidden');
        document.getElementById('controlPanel').classList.add('hidden');
    }
}

function showConnectedUI() {
    console.log("✅ Connected to backend - updating UI");
    
    document.getElementById('connectionDot').className = 'w-3 h-3 bg-green-500 rounded-full pulse-glow';
    document.getElementById('connectionText').textContent = 'Connected to Auto Clicker Backend';
    document.getElementById('connectionText').className = 'text-green-300 font-semibold';
    document.getElementById('connectionInfo').textContent = 'Connected • Backend Active';
    document.getElementById('serviceStatus').className = 'w-2 h-2 bg-green-500 rounded-full';
    
    document.getElementById('downloadSection').classList.add('hidden');
    document.getElementById('controlPanel').classList.remove('hidden');
}

function showDisconnectedUI() {
    console.log("❌ Disconnected from backend - updating UI");
    
    document.getElementById('connectionDot').className = 'w-3 h-3 bg-red-500 rounded-full pulse-glow';
    document.getElementById('connectionText').textContent = 'Searching for Auto Clicker Backend...';
    document.getElementById('connectionText').className = 'text-red-300 font-semibold';
    document.getElementById('connectionInfo').textContent = 'Disconnected • Check if backend is running';
    document.getElementById('serviceStatus').className = 'w-2 h-2 bg-red-500 rounded-full';
    
    document.getElementById('downloadSection').classList.remove('hidden');
    document.getElementById('controlPanel').classList.add('hidden');
}

function updateUI() {
    if (!isConnected) return;
    
    console.log("🔄 Updating UI with status:", currentStatus);
    
    // Update running state
    isRunning = currentStatus.running;
    
    // Update status display
    document.getElementById('intervalValue').textContent = Number(currentStatus.interval).toFixed(3);
    document.getElementById('statusText').textContent = isRunning ? "RUNNING" : "STOPPED";
    document.getElementById('statusText').className = `text-2xl font-bold font-['Orbitron'] ${
        isRunning ? 'text-green-400' : 'text-red-400'
    }`;
    document.getElementById('statusIndicator').className = `w-5 h-5 rounded-full mx-auto mb-4 border-2 border-white/30 ${
        isRunning ? 'bg-green-500' : 'bg-red-500'
    }`;
    
    document.getElementById('actionCount').textContent = currentStatus.actions;
    document.getElementById('sessionTime').textContent = currentStatus.session_time + "s";

    // Update toggles
    document.getElementById('jitterToggle').checked = currentStatus.jitter_enabled;
    document.getElementById('humanLikeToggle').checked = currentStatus.human_like;

    // Update active mode
    document.querySelectorAll(".mode-btn").forEach(btn => {
        btn.classList.remove("mode-active");
        if (btn.dataset.mode === currentStatus.mode) {
            btn.classList.add("mode-active");
        }
    });

    // Update button states
    updateButtonStates();
    
    // Update CPS display
    updateCPSDisplay();
    
    // Update slider position
    updateSliderPosition();
}

function updateButtonStates() {
    const toggleBtn = document.getElementById('toggleBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    if (isRunning) {
        // When running: grey out start button, enable stop button
        toggleBtn.innerHTML = '<i class="fas fa-play mr-3"></i>START AUTO CLICKER (F6)';
        toggleBtn.classList.remove('start-btn', 'pulse-glow');
        toggleBtn.classList.add('btn-greyed');
        toggleBtn.style.borderColor = 'rgba(107, 114, 128, 0.3)';
        
        stopBtn.classList.remove('btn-disabled');
        stopBtn.classList.add('stop-btn');
    } else {
        // When stopped: enable start button, grey out stop button
        toggleBtn.innerHTML = '<i class="fas fa-play mr-3"></i>START AUTO CLICKER (F6)';
        toggleBtn.classList.remove('btn-greyed');
        toggleBtn.classList.add('start-btn', 'pulse-glow');
        toggleBtn.style.borderColor = 'rgba(34, 197, 94, 0.3)';
        
        stopBtn.classList.remove('stop-btn');
        stopBtn.classList.add('btn-disabled');
    }
}

function updateCPSDisplay() {
    const interval = currentStatus.interval;
    const cps = interval > 0 ? (1 / interval).toFixed(1) : "∞";
    document.getElementById('cpsValue').textContent = `${cps} CPS`;
}

function updateSliderPosition() {
    const interval = currentStatus.interval;
    const sliderValue = Math.max(1, Math.min(200, Math.round(interval * 100)));
    document.querySelector('.slider').value = sliderValue;
}

async function sendCommand(command, extra = {}) {
    if (!isConnected) {
        showNotification("⚠️ Not connected to backend. Please check if the Auto Clicker application is running.", "error");
        console.warn("⚠️ Not connected, skipping command:", command);
        return null;
    }
    
    console.log("📤 Sending command:", command, extra);
    
    try {
        const response = await fetch("http://localhost:8080/command", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ command, ...extra })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log("📥 Command response:", data);
        
        return data;
        
    } catch (err) {
        console.error("❌ Command failed:", err);
        showNotification(`❌ Command failed: ${err.message}`, "error");
        return null;
    }
}

// Command functions
function toggleAutoClicker() { 
    sendCommand("toggle_running"); 
}

function stopAutoClicker() { 
    if (isRunning) {
        sendCommand("toggle_running");
    }
}

function setMode(m) { 
    sendCommand("set_mode", { mode: m }); 
}

function updateInterval(sliderValue) {
    const interval = Math.max(0.005, sliderValue / 100);
    document.getElementById('intervalValue').textContent = interval.toFixed(3);
    updateCPSDisplay();
    sendCommand("set_interval", { interval: interval });
}

function setJitter(e) { 
    sendCommand("set_jitter", { enabled: e }); 
}

function setHumanLike(e) { 
    sendCommand("set_human_like", { enabled: e }); 
}

function setCustomKey() {
    const k = prompt("Enter custom key (e.g., 'a', 'enter', 'space'):");
    if (k) sendCommand("set_custom_key", { key: k });
}

// Debug functions
async function testWindowsKey() {
    console.log("🪟 Testing Windows key press...");
    const result = await sendCommand("debug_windows_key");
    if (result && result.status === "ok") {
        showNotification("✅ Windows key pressed successfully!", "success");
    } else {
        showNotification("❌ Failed to press Windows key", "error");
    }
}

async function testSingleClick() {
    console.log("🖱️ Testing single click...");
    const result = await sendCommand("debug_single_click");
    if (result && result.status === "ok") {
        showNotification("✅ Single click performed!", "success");
    } else {
        showNotification("❌ Failed to perform click", "error");
    }
}

// Initialize connection
console.log("🚀 Auto Clicker Pro Web Interface starting...");

// Try WebSocket first, fallback to polling
connectWebSocket();

// Also start polling as initial connection method
setTimeout(checkBackendConnection, 100);

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
    }
    if (websocket) {
        websocket.close();
    }
    if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
    }
});
