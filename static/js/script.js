document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    const clearButton = document.getElementById('clear-chat');
    const exportButton = document.getElementById('export-chat');
    const themeSwitch = document.getElementById('theme-switch');
    const typingIndicator = document.getElementById('typing-indicator');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const appTitle = document.querySelector('.app-title');
    const chatInput = document.querySelector('.chat-input');
    
    // Function to toggle mic button visibility
    function toggleMicButton() {
        if (userInput.value.trim() !== '') {
            micButton.classList.add('hide-mic');
        } else {
            micButton.classList.remove('hide-mic');
        }
    }
    
    // Check mic visibility on input changes
    userInput.addEventListener('input', toggleMicButton);
    
    // Reset mic visibility when sending a message
    function resetInputAndMic() {
        userInput.value = '';
        toggleMicButton();
    }
    
    // Speech recognition setup
    let recognition = null;
    let isRecording = false;
    
    // Check if browser supports speech recognition
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
            isRecording = true;
            micButton.classList.add('recording');
            showToast('Listening...', false, 10000);
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            setTimeout(() => {
                sendMessage();
            }, 500);
        };
        
        recognition.onend = () => {
            isRecording = false;
            micButton.classList.remove('recording');
            document.getElementById('toast').classList.remove('show');
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            isRecording = false;
            micButton.classList.remove('recording');
            showToast('Speech recognition error. Please try again.', true);
        };
    } else {
        micButton.style.display = 'none';
        console.log('Speech recognition not supported in this browser');
    }
    
    // Initialize animations for title letters with staggered delay
    const animateTitle = () => {
        const letters = document.querySelectorAll('.animated-letter');
        letters.forEach((letter, index) => {
            letter.style.animationDelay = `${index * 0.1}s`;
        });
    };
    
    // Run title animation
    animateTitle();
    
    // Add focus effect to the chat input
    userInput.addEventListener('focus', () => {
        chatInput.classList.add('input-focus-effect');
    });
    
    userInput.addEventListener('blur', () => {
        chatInput.classList.remove('input-focus-effect');
    });
    
    // Microphone button click event
    micButton.addEventListener('click', () => {
        if (!recognition) {
            showToast('Speech recognition not supported in your browser', true);
            return;
        }
        
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
    
    // Chat history array to store messages for export
    let chatHistory = [{
        sender: 'bot',
        content: `<strong>Welcome to the Nutrition Facts Guide!</strong><br><br>
        I'm your personal nutrition assistant. I can help you with information about food nutrients, calories, dietary information, and health benefits of different foods.<br><br>
        <strong>Here are some things you can ask me:</strong><br>
        • What are the nutrition facts in an apple?<br>
        • How many calories are in a banana?<br>
        • What nutrients are in salmon?<br>
        • Tell me about the health benefits of spinach<br>
        • Is oatmeal good for breakfast?<br>
        • Compare nutritional value of white rice vs brown rice<br><br>
        What would you like to know about today?`
    }];
    
    // Ensure welcome message is visible
    function ensureWelcomeMessage() {
        // Check if welcome message exists
        const welcomeMsg = document.querySelector('.welcome-message');
        if (!welcomeMsg || welcomeMsg.style.display === 'none') {
            // Add welcome message if it doesn't exist
            const welcomeContent = `<strong>Welcome to the Nutrition Facts Guide!</strong><br><br>
            I'm your personal nutrition assistant. I can help you with information about food nutrients, calories, dietary information, and health benefits of different foods.<br><br>
            <strong>Here are some things you can ask me:</strong><br>
            • What are the nutrition facts in an apple?<br>
            • How many calories are in a banana?<br>
            • What nutrients are in salmon?<br>
            • Tell me about the health benefits of spinach<br>
            • Is oatmeal good for breakfast?<br>
            • Compare nutritional value of white rice vs brown rice<br><br>
            What would you like to know about today?`;
            addMessage(welcomeContent, 'bot', true);
        } else {
            // If welcome message exists but no suggestion buttons, add them
            const existingSuggestions = document.querySelector('.suggestion-buttons');
            if (!existingSuggestions) {
                addSuggestionButtons();
            }
        }
    }
    
    // Call this function to ensure welcome message is displayed
    ensureWelcomeMessage();
    
    // Theme handling
    themeSwitch.addEventListener('change', () => {
        document.body.classList.toggle('dark-theme');
        localStorage.setItem('darkTheme', themeSwitch.checked);
    });
    
    // Check user preference
    if (localStorage.getItem('darkTheme') === 'true') {
        themeSwitch.checked = true;
        document.body.classList.add('dark-theme');
    }
    
    // Send message when click send button
    sendButton.addEventListener('click', () => {
        sendMessage();
    });
    
    // Send message when press Enter
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Clear chat
    clearButton.addEventListener('click', () => {
        clearChat();
    });
    
    // Export chat functionality
    exportButton.addEventListener('click', () => {
        exportChat();
    });
    
    // Initialize animations for smoother experience
    animateBackground();
    
    // Function to check if query is about specific food facts
    function isFoodFactQuery(query) {
        const foodFactPatterns = [
            /nutrition( facts| information)? (of|in|for) ([a-z\s]+)/i,
            /calories (of|in|for) ([a-z\s]+)/i,
            /nutrients (of|in|for) ([a-z\s]+)/i,
            /tell me about ([a-z\s]+) nutrition/i,
            /what('s| is) in ([a-z\s]+)/i,
            /what are the nutrients in ([a-z\s]+)/i
        ];
        
        return foodFactPatterns.some(pattern => pattern.test(query));
    }
    
    // Function to check if message is a greeting
    function isGreeting(message) {
        const greetingWords = [
            'hi', 'hello', 'hey', 'greetings', 'howdy', 'hola', 'namaste', 
            'good morning', 'good afternoon', 'good evening', 'good day',
            'what\'s up', 'sup', 'yo', 'hiya', 'hi there', 'hello there',
            'morning', 'evening', 'afternoon', 'welcome', 'bonjour', 'ciao'
        ];
        
        const messageWords = message.toLowerCase().split(/\s+/);
        return messageWords.some(word => greetingWords.includes(word)) || 
               greetingWords.includes(message.toLowerCase());
    }
    
    // Extract food name from query
    function extractFoodName(query) {
        const patterns = [
            /nutrition( facts| information)? (of|in|for) ([a-z\s]+)$/i,
            /calories (of|in|for) ([a-z\s]+)$/i,
            /nutrients (of|in|for) ([a-z\s]+)$/i,
            /tell me about ([a-z\s]+) nutrition/i,
            /what('s| is) in ([a-z\s]+)$/i,
            /what are the nutrients in ([a-z\s]+)$/i
        ];
        
        for (const pattern of patterns) {
            const match = query.match(pattern);
            if (match) {
                // The food name will be in the last capturing group
                return match[match.length - 1].trim();
            }
        }
        
        // If no pattern matched, try to extract words after common prepositions
        const words = query.split(' ');
        for (let i = 0; i < words.length; i++) {
            if (['in', 'of', 'about', 'for'].includes(words[i].toLowerCase())) {
                if (i < words.length - 1) {
                    return words.slice(i + 1).join(' ');
                }
            }
        }
        
        return null;
    }
    
    // Function to get food information directly from API
    async function getFoodInfo(foodName) {
        try {
            const response = await fetch(`/api/food_info?food_name=${encodeURIComponent(foodName)}`);
            if (!response.ok) {
                throw new Error('Food not found or error fetching data');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching food info:', error);
            return null;
        }
    }
    
    // Functions
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Add to chat history
        chatHistory.push({
            sender: 'user',
            content: message
        });
        
        // Clear input field and reset mic button
        resetInputAndMic();
        
        // Show typing indicator
        showTypingIndicator();
        
        // Check if it's a greeting (handle client-side for faster response)
        if (isGreeting(message)) {
            setTimeout(() => {
                hideTypingIndicator();
                const welcomeMessage = `<strong>Welcome to the Nutrition Facts Guide!</strong><br><br>
                I'm your personal nutrition assistant. I can help you with information about food nutrients, calories, dietary information, and health benefits of different foods.<br><br>
                <strong>Here are some things you can ask me:</strong><br>
                • What are the nutrition facts in an apple?<br>
                • How many calories are in a banana?<br>
                • What nutrients are in salmon?<br>
                • Tell me about the health benefits of spinach<br>
                • Is oatmeal good for breakfast?<br>
                • Compare nutritional value of white rice vs brown rice<br><br>
                What would you like to know about today?`;
                
                addMessage(welcomeMessage, 'bot');
                
                // Add to chat history
                chatHistory.push({
                    sender: 'bot',
                    content: welcomeMessage
                });
            }, 600); // Add a small delay to simulate typing
            return;
        }
        
        // Check if it's a food fact query
        if (isFoodFactQuery(message)) {
            const foodName = extractFoodName(message);
            if (foodName) {
                try {
                    const foodInfo = await getFoodInfo(foodName);
                    hideTypingIndicator();
                    
                    if (foodInfo && !foodInfo.error) {
                        const formattedResponse = foodInfo.formatted || 
                            `<strong>Information about ${foodName}</strong><br>Sorry, I couldn't find detailed nutrition information for this food.`;
                        
                        addMessage(formattedResponse, 'bot');
                        
                        // Add to chat history
                        chatHistory.push({
                            sender: 'bot',
                            content: formattedResponse
                        });
                        return;
                    }
                } catch (error) {
                    console.error('Error processing food query:', error);
                    // Fall through to regular API
                }
            }
        }
        
        // Send message to server (regular API)
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            hideTypingIndicator();
            
            // Add bot response to chat
            if (data.exit) {
                addMessage(data.response, 'bot');
                
                // Add to chat history
                chatHistory.push({
                    sender: 'bot',
                    content: data.response
                });
                
                setTimeout(() => {
                    alert('Session ended. Refresh to start a new chat.');
                }, 1000);
            } else {
                addMessage(data.response, 'bot');
                
                // Add to chat history
                chatHistory.push({
                    sender: 'bot',
                    content: data.response
                });
            }
        })
        .catch(error => {
            hideTypingIndicator();
            console.error('Error:', error);
            const errorMessage = 'Sorry, there was an error communicating with the server. Please try again.';
            addMessage(errorMessage, 'bot');
            
            // Add to chat history
            chatHistory.push({
                sender: 'bot',
                content: errorMessage
            });
        });
    }
    
    function addMessage(content, sender, isWelcome = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        // If it's welcome message, add the welcome class
        if (isWelcome) {
            messageDiv.classList.add('welcome-message');
        }
        
        // Create avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('message-avatar');
        
        const avatarIcon = document.createElement('i');
        if (sender === 'user') {
            avatarIcon.classList.add('fas', 'fa-user');
        } else {
            avatarIcon.classList.add('fas', 'fa-robot');
        }
        avatarDiv.appendChild(avatarIcon);
        
        // Create message content
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        // Handle content (check if it contains HTML)
        if (sender === 'bot' && (content.includes('<br>') || content.includes('<strong>') || content.includes('<em>'))) {
            contentDiv.innerHTML = content;
        } else {
            const paragraph = document.createElement('p');
            paragraph.textContent = content;
            contentDiv.appendChild(paragraph);
        }
        
        // Assemble message
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        // Add to chat
        chatMessages.appendChild(messageDiv);
        
        // If this is a welcome or greeting response, add suggestion buttons
        if (sender === 'bot' && (isWelcome || content.includes('Here are some things you can ask me'))) {
            addSuggestionButtons();
        }
        
        // Auto scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add entrance animation
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
    }
    
    // Function to add clickable suggestion buttons
    function addSuggestionButtons() {
        const suggestions = [
            'What are the nutrition facts in an apple?',
            'How many calories are in a banana?',
            'What nutrients are in salmon?',
            'Tell me about the health benefits of spinach',
            'Is oatmeal good for breakfast?',
            'Compare nutritional value of white rice vs brown rice'
        ];
        
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.classList.add('suggestion-buttons');
        
        suggestions.forEach(suggestion => {
            const button = document.createElement('button');
            button.classList.add('suggestion-button');
            button.textContent = suggestion;
            
            button.addEventListener('click', () => {
                userInput.value = suggestion;
                sendMessage();
            });
            
            suggestionsDiv.appendChild(button);
        });
        
        chatMessages.appendChild(suggestionsDiv);
        
        // Auto scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add entrance animation
        setTimeout(() => {
            suggestionsDiv.style.opacity = '1';
            suggestionsDiv.style.transform = 'translateY(0)';
        }, 10);
    }
    
    function showTypingIndicator() {
        typingIndicator.classList.remove('hidden');
        setTimeout(() => {
            typingIndicator.classList.add('visible');
        }, 10);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function hideTypingIndicator() {
        typingIndicator.classList.remove('visible');
        setTimeout(() => {
            typingIndicator.classList.add('hidden');
        }, 300);
    }
    
    function clearChat() {
        // Keep only welcome message
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        
        // Reset chat history
        chatHistory = [{
            sender: 'bot',
            content: `<strong>Welcome to the Nutrition Facts Guide!</strong><br><br>
            I'm your personal nutrition assistant. I can help you with information about food nutrients, calories, dietary information, and health benefits of different foods.<br><br>
            <strong>Here are some things you can ask me:</strong><br>
            • What are the nutrition facts in an apple?<br>
            • How many calories are in a banana?<br>
            • What nutrients are in salmon?<br>
            • Tell me about the health benefits of spinach<br>
            • Is oatmeal good for breakfast?<br>
            • Compare nutritional value of white rice vs brown rice<br><br>
            What would you like to know about today?`
        }];
        
        // Show toast
        showToast('Chat cleared successfully!');
    }
    
    function exportChat() {
        if (chatHistory.length <= 1) {
            showToast('Nothing to export yet!', true);
            return;
        }
        
        const content = chatHistory.map(msg => {
            const sender = msg.sender === 'user' ? 'You' : 'Nutrition Guide';
            return `${sender}: ${msg.content.replace(/<[^>]*>/g, '')}`;
        }).join('\n\n');
        
        const date = new Date().toISOString().slice(0, 10);
        const filename = `nutrition-chat-${date}.txt`;
        
        // Create blob and download
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
        
        // Show toast
        showToast('Chat exported successfully!');
    }
    
    // Show toast notification
    function showToast(message, isError = false, duration = 3000) {
        toastMessage.textContent = message;
        toast.classList.add('show');
        
        if (isError) {
            toast.classList.add('error');
        } else {
            toast.classList.remove('error');
        }
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, duration);
    }
    
    function animateBackground() {
        // This is just a placeholder for any additional background animations
        // The CSS already handles most of the animation
        
        // You could add dynamic blob creation or additional effects here
        // For example, creating new blobs on user interaction
        document.addEventListener('click', function(e) {
            // Add a mini blob effect on click (optional enhancement)
            if (e.target.closest('.chat-container') || e.target.closest('.app-title-container')) {
                return; // Don't create click effects in these areas
            }
            
            // Create a small temporary blob effect at click position
            const miniBlob = document.createElement('div');
            miniBlob.classList.add('mini-blob');
            miniBlob.style.left = `${e.clientX}px`;
            miniBlob.style.top = `${e.clientY}px`;
            document.body.appendChild(miniBlob);
            
            // Remove after animation completes
            setTimeout(() => {
                document.body.removeChild(miniBlob);
            }, 1000);
        });
    }
    
    // API Test at startup
    fetch('/api/test')
        .then(response => response.json())
        .then(data => {
            console.log('API Status:', data.message);
        })
        .catch(error => {
            console.error('API Error:', error);
        });
}); 