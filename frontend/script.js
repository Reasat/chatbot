// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let isConnected = false;
let knowledgeBaseLoaded = false;

// DOM Elements
const statusIndicator = document.getElementById('statusIndicator');
const statusDot = statusIndicator.querySelector('.status-dot');
const statusText = statusIndicator.querySelector('.status-text');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const kbStatus = document.getElementById('kbStatus');
const kbInfo = document.getElementById('kbInfo');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const ragToggle = document.getElementById('ragToggle');
const responseModal = document.getElementById('responseModal');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkConnection();
    setupEventListeners();
    checkKnowledgeBaseStatus();
});

// Event Listeners
function setupEventListeners() {
    // File upload
    fileInput.addEventListener('change', handleFileUpload);
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Chat
    messageInput.addEventListener('keypress', handleKeyPress);
    sendButton.addEventListener('click', sendMessage);
    
    // Modal
    window.addEventListener('click', function(event) {
        if (event.target === responseModal) {
            closeModal();
        }
    });
}

// Connection Management
async function checkConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            setConnected(true);
        } else {
            setConnected(false);
        }
    } catch (error) {
        setConnected(false);
        console.error('Connection check failed:', error);
    }
}

function setConnected(connected) {
    isConnected = connected;
    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// File Upload
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

async function uploadFile(file) {
    if (!file.name.endsWith('.json')) {
        showError('Please upload a JSON file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading('Uploading knowledge base...');
        
        const response = await fetch(`${API_BASE_URL}/upload-knowledge-base`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showKnowledgeBaseStatus(result);
            addMessage('bot', 'Knowledge base uploaded successfully! You can now ask questions about the data.');
        } else {
            const error = await response.json();
            showError(`Upload failed: ${error.detail}`);
        }
    } catch (error) {
        showError('Upload failed. Please check your connection.');
        console.error('Upload error:', error);
    }
    
    hideLoading();
}

// Knowledge Base Status
async function checkKnowledgeBaseStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge-base-status`);
        if (response.ok) {
            const status = await response.json();
            if (status.loaded) {
                showKnowledgeBaseStatus(status);
            }
        }
    } catch (error) {
        console.error('Status check failed:', error);
    }
}

function showKnowledgeBaseStatus(status) {
    knowledgeBaseLoaded = status.loaded;
    uploadArea.style.display = 'none';
    kbStatus.style.display = 'block';
    kbInfo.textContent = `${status.chunks_count} chunks loaded`;
}

// Chat Functions
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message
    addMessage('user', message);
    messageInput.value = '';
    
    // Disable input while processing
    setInputEnabled(false);
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                use_rag: ragToggle.checked
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            addBotMessage(result.response, result.sources, result.confidence, result.processing_time);
        } else {
            const error = await response.json();
            addMessage('bot', `Error: ${error.detail}`);
        }
    } catch (error) {
        addMessage('bot', 'Sorry, I encountered an error. Please check your connection.');
        console.error('Chat error:', error);
    }
    
    setInputEnabled(true);
}

function addMessage(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const icon = type === 'user' ? 'fas fa-user' : 'fas fa-robot';
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="${icon}"></i>
            <div class="text">${escapeHtml(text)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addBotMessage(text, sources, confidence, processingTime) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    let detailsHtml = '';
    if (sources && sources.length > 0) {
        detailsHtml = `<div class="response-details" onclick="showResponseDetails('${escapeHtml(JSON.stringify({sources, confidence, processingTime}))}')">View details</div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="fas fa-robot"></i>
            <div class="text">${escapeHtml(text)}${detailsHtml}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showResponseDetails(detailsJson) {
    const details = JSON.parse(detailsJson);
    
    // Populate sources
    const sourcesList = document.getElementById('sourcesList');
    sourcesList.innerHTML = '';
    
    if (details.sources && details.sources.length > 0) {
        details.sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.innerHTML = `
                <div class="source-key">${escapeHtml(source.key_path)}</div>
                <div class="source-content">${escapeHtml(source.content)}</div>
            `;
            sourcesList.appendChild(sourceItem);
        });
    } else {
        sourcesList.innerHTML = '<p>No sources used</p>';
    }
    
    // Update confidence
    const confidencePercent = Math.round(details.confidence * 100);
    document.getElementById('confidenceFill').style.width = `${confidencePercent}%`;
    document.getElementById('confidenceText').textContent = `${confidencePercent}%`;
    
    // Update processing time
    document.getElementById('processingTime').textContent = `${Math.round(details.processing_time * 1000)}ms`;
    
    // Show modal
    responseModal.style.display = 'block';
}

function closeModal() {
    responseModal.style.display = 'none';
}

// Utility Functions
function setInputEnabled(enabled) {
    messageInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    addMessage('bot', `❌ ${message}`);
}

function showLoading(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="fas fa-robot"></i>
            <div class="text">
                <div class="loading"></div> ${message}
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function hideLoading() {
    // Remove the last bot message (loading message)
    const messages = chatMessages.querySelectorAll('.bot-message');
    if (messages.length > 0) {
        messages[messages.length - 1].remove();
    }
} 