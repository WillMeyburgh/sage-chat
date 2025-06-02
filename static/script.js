document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const sageList = document.getElementById('sage-list');
    const currentSageName = document.getElementById('current-sage-name');
    const currentSagePortrait = document.getElementById('current-sage-portrait');

    let selectedSage = 'Socrates'; // Initialize with Socrates as the default sage

    // Function to fetch and display initial message
    function fetchInitialMessage(sageName) {
        fetch('/get_initial_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sage: sageName }),
        })
        .then(response => response.json())
        .then(data => {
            appendMessage(data.initial_message, 'sage-message');
        })
        .catch(error => {
            console.error('Error fetching initial message:', error);
            appendMessage('Error: Could not get initial message from the sage.', 'sage-message');
        });
    }

    // Function to update the header with selected sage's name and portrait
    function updateHeader(sageName, portraitUrl) {
        currentSageName.textContent = sageName;
        if (portraitUrl) {
            currentSagePortrait.src = portraitUrl;
            currentSagePortrait.classList.remove('d-none');
        } else {
            currentSagePortrait.classList.add('d-none');
        }
    }

    // Function to fetch and populate sage list
    function populateSageList() {
        fetch('/get_sages')
            .then(response => response.json())
            .then(sages => {
                sageList.innerHTML = ''; // Clear existing list items
                sages.forEach(sage => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('nav-item');
                    const link = document.createElement('a');
                    link.href = '#';
                    link.classList.add('nav-link', 'text-dark', 'sage-item');
                    link.setAttribute('data-sage', sage.name);
                    const img = document.createElement('img');
                    img.src = sage.portrait_url;
                    img.alt = sage.name;
                    img.width = 24;
                    img.height = 24;
                    img.classList.add('rounded-circle', 'me-2');
                    img.onerror = function() {
                        this.onerror=null; // Prevent infinite loop if fallback also fails
                        this.outerHTML = '<i class="fas fa-user-circle me-2"></i>'; // Replace with Font Awesome icon
                    };
                    link.appendChild(img);
                    
                    const span = document.createElement('span');
                    span.textContent = sage.name;
                    link.appendChild(span);
                    
                    if (sage.name === selectedSage) {
                        link.classList.add('active');
                        updateHeader(selectedSage, sage.portrait_url); // Set initial header
                        userInput.placeholder = `Chat with ${selectedSage}...`; // Set initial placeholder
                    }
                    listItem.appendChild(link);
                    sageList.appendChild(listItem);
                });
                // Ensure Socrates is active and header is set if no other sage is selected
                const socratesLink = document.querySelector(`.sage-item[data-sage="Socrates"]`);
                if (socratesLink && !document.querySelector('.sage-item.active')) {
                    socratesLink.classList.add('active');
                    selectedSage = 'Socrates';
                    const socratesPortraitUrl = socratesLink.querySelector('img') ? socratesLink.querySelector('img').src : '';
                    updateHeader(selectedSage, socratesPortraitUrl);
                    userInput.placeholder = `Chat with ${selectedSage}...`; // Set initial placeholder for Socrates
                }
                fetchInitialMessage(selectedSage); // Fetch initial message for the selected sage
            })
            .catch(error => {
                console.error('Error fetching sages:', error);
                appendMessage('Error: Could not load sages list. Using default Socrates.', 'sage-message');
                // Fallback if sages list cannot be loaded
                updateHeader('Socrates', "/static/img/socrates.jpg"); // Use local fallback portrait
                userInput.placeholder = `Chat with Socrates...`; // Set placeholder for Socrates fallback
                fetchInitialMessage('Socrates');
            });
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    sageList.addEventListener('click', (e) => {
        const target = e.target.closest('.sage-item'); // Use closest to handle clicks on children (img, span)
        if (target) {
            // Remove active class from previous sage
            const currentActive = document.querySelector('.sage-item.active');
            if (currentActive) {
                currentActive.classList.remove('active');
            }
            // Add active class to clicked sage
            target.classList.add('active');
            selectedSage = target.dataset.sage;
            
            const portraitImg = target.querySelector('img');
            const portraitUrl = portraitImg ? portraitImg.src : '';
            updateHeader(selectedSage, portraitUrl);
            
            chatBox.innerHTML = ''; // Clear chat history for new sage
            fetchInitialMessage(selectedSage); // Fetch and display new sage's initial message
            userInput.placeholder = `Chat with ${selectedSage}...`; // Update placeholder text
        }
    });

    // Initial population and message when page loads
    populateSageList();

    function appendTypingIndicator() {
        const indicatorElement = document.createElement('div');
        indicatorElement.classList.add('message', 'sage-message', 'typing-indicator');
        indicatorElement.innerHTML = `
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        `;
        chatBox.appendChild(indicatorElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        appendMessage(message, 'user-message');
        userInput.value = '';

        appendTypingIndicator(); // Show typing indicator

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message, sage: selectedSage }), // Send selected sage to backend
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator(); // Remove typing indicator
            appendMessage(data.response, 'sage-message');
        })
        .catch(error => {
            removeTypingIndicator(); // Remove typing indicator even on error
            console.error('Error:', error);
            appendMessage('Error: Could not connect to the sage.', 'sage-message');
        });
    }

    function appendMessage(message, type) {
        const placeholder = document.getElementById('empty-chat-placeholder');
        if (placeholder) {
            placeholder.remove();
        }

        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
    }

    // Also remove placeholder when user sends a message
    sendButton.addEventListener('click', () => {
        const placeholder = document.getElementById('empty-chat-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        sendMessage();
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const placeholder = document.getElementById('empty-chat-placeholder');
            if (placeholder) {
                placeholder.remove();
            }
            sendMessage();
        }
    });
});
