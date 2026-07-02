document.addEventListener('DOMContentLoaded', () => {
    // Connect to Socket.IO server
    const socket = io();

    // DOM Elements
    const statusOrb = document.getElementById('status-orb');
    const statusText = document.getElementById('status-text');
    const chatBox = document.getElementById('chat-box');
    const updateBtn = document.getElementById('update-btn');

    // State mapping for the UI
    const stateMap = {
        'STARTING': { class: 'asleep', text: 'Starting Pipeline...' },
        'ASLEEP': { class: 'asleep', text: 'Asleep (Waiting for Wakeword)' },
        'LISTENING': { class: 'listening', text: 'Listening...' },
        'THINKING': { class: 'thinking', text: 'Thinking...' },
        'SPEAKING': { class: 'speaking', text: 'Speaking' }
    };

    // Fetch models on connection
    socket.on('connect', () => {
        socket.emit('get_models');
    });

    // Populate LLM dropdown
    socket.on('models_list', (models) => {
        const llmSelect = document.getElementById('llm-model');
        llmSelect.innerHTML = '';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.innerText = model;
            llmSelect.appendChild(option);
        });
    });

    // Listen for Status Updates
    socket.on('status', (data) => {
        const state = stateMap[data] || stateMap['ASLEEP'];
        
        // Update Orb Class
        statusOrb.className = 'orb';
        statusOrb.classList.add(state.class);
        
        // Update Text
        statusText.innerText = state.text;
    });

    // Listen for Transcripts (User and Robot)
    socket.on('transcript', (data) => {
        const { role, text } = data;
        
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', role); // role is 'user' or 'robot'
        messageDiv.innerText = text;
        
        chatBox.appendChild(messageDiv);
        
        // Auto-scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // Update Settings Button
    updateBtn.addEventListener('click', () => {
        const llmModel = document.getElementById('llm-model').value;
        const ipWebcam = document.getElementById('ip-webcam').value;
        const asrLang = document.getElementById('asr-lang').value;
        const ttsLang = document.getElementById('tts-lang').value;
        
        updateBtn.innerText = "Applying...";
        updateBtn.style.opacity = "0.7";
        
        // Send settings to backend (future expansion)
        socket.emit('update_settings', {
            llm_model: llmModel,
            ip_stream_url: ipWebcam,
            asr_lang: asrLang,
            tts_lang: ttsLang
        });

        // Simulate network delay for UX
        setTimeout(() => {
            updateBtn.innerText = "Apply Settings";
            updateBtn.style.opacity = "1";
            
            const sysMsg = document.createElement('div');
            sysMsg.classList.add('message', 'system');
            sysMsg.innerText = "Settings updated successfully.";
            chatBox.appendChild(sysMsg);
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 800);
    });
});
