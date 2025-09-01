function sendToBot(action, data = {}) {
    if (Telegram.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify({ action, ...data }));
    }
}

// Navigation bar logic
document.querySelectorAll('.nav-btn').forEach(button => {
    button.addEventListener('click', (event) => {
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        event.currentTarget.classList.add('active');
        
        const targetSection = event.currentTarget.dataset.section;
        document.querySelectorAll('main section').forEach(section => {
            section.classList.remove('active-section');
            section.classList.add('hidden');
        });
        document.getElementById(`${targetSection}-section`).classList.remove('hidden');
        document.getElementById(`${targetSection}-section`).classList.add('active-section');

        sendToBot('get_user_info');
    });
});

// Button click handlers
document.getElementById('watch-ad-btn').addEventListener('click', () => {
    sendToBot('watch_ad');
});

document.getElementById('checkin-btn').addEventListener('click', () => {
    sendToBot('claim_daily_checkin');
});

document.getElementById('get-referral-link').addEventListener('click', () => {
    sendToBot('get_referral_link');
});

document.getElementById('swap-to-usdt-btn').addEventListener('click', () => {
    sendToBot('swap_points_to_usdt');
});

document.getElementById('binance-btn').addEventListener('click', () => {
    sendToBot('start_withdrawal', { method: 'binance' });
});

document.getElementById('trust-wallet-btn').addEventListener('click', () => {
    sendToBot('start_withdrawal', { method: 'trust_wallet' });
});

window.onload = () => {
    if (Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user) {
        document.getElementById('user-id').textContent = `ID: ${Telegram.WebApp.initDataUnsafe.user.id}`;
    }
    sendToBot('get_user_info');
};

Telegram.WebApp.onEvent('onReceivedData', (data) => {
    // This part would be used to update UI dynamically.
    // For now, we are sending messages to chat.
});
