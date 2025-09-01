// Function to send data to the bot
function sendToBot(action, data = {}) {
    if (Telegram.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify({ action, ...data }));
    }
}

// Function to update the UI based on data received from the bot
function updateUI(data) {
    if (data.user_id) {
        document.getElementById('user-id').textContent = `ID: ${data.user_id}`;
    }
    if (data.points !== undefined) {
        document.getElementById('balance').textContent = `BALANCE: ${data.points} POINTS`;
    }
    if (data.daily_watched !== undefined) {
        document.getElementById('daily-watched').textContent = data.daily_watched;
        const progressPercentage = (data.daily_watched / 30) * 100;
        document.getElementById('daily-progress').style.width = `${progressPercentage}%`;
    }
    if (data.referral_code) {
        document.getElementById('referral-link').textContent = `https://t.me/${Telegram.WebApp.initDataUnsafe.user.username}?start=${data.referral_code}`;
    }
    if (data.bonus_status) {
        document.getElementById('bonus-status').textContent = `Daily Bonus: ${data.bonus_status}`;
        if (data.bonus_status !== 'Not claimed yet') {
            document.getElementById('claim-bonus-btn').disabled = true;
            document.getElementById('claim-bonus-btn').textContent = 'Already Claimed';
        }
    }
}

// Button click handlers
document.getElementById('watch-ad-btn').addEventListener('click', () => {
    // Send a request to the bot to process an ad watch
    sendToBot('watch_ad');
    Telegram.WebApp.close();
});

document.getElementById('claim-bonus-btn').addEventListener('click', () => {
    sendToBot('claim_daily_bonus');
    Telegram.WebApp.close();
});

document.getElementById('copy-referral').addEventListener('click', () => {
    const link = document.getElementById('referral-link').textContent;
    navigator.clipboard.writeText(link).then(() => {
        alert('Referral link copied to clipboard!');
    });
});

document.getElementById('withdraw-btn').addEventListener('click', () => {
    sendToBot('start_withdrawal');
    Telegram.WebApp.close();
});

// Navigation bar logic
document.querySelectorAll('.nav-btn').forEach(button => {
    button.addEventListener('click', (event) => {
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        event.currentTarget.classList.add('active');
        
        const targetSection = event.currentTarget.dataset.section;
        document.querySelectorAll('main section').forEach(section => {
            section.classList.add('hidden');
        });
        document.getElementById(`${targetSection}-section`).classList.remove('hidden');

        // Request initial data from the bot for the new section
        if (targetSection === 'info') {
            sendToBot('get_user_info');
        }
    });
});

// Request initial data from the bot when the page loads
window.onload = () => {
    // We will not close the app here
};

// Listen for messages from the bot (this is a placeholder for a more advanced setup)
Telegram.WebApp.onEvent('onReceivedData', (data) => {
    updateUI(data);
});
