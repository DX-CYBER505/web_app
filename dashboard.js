// Function to send data to the bot
function sendToBot(action, data = {}) {
    if (Telegram.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify({ action, ...data }));
    }
}

// Handle all button clicks from the dashboard
document.getElementById('watch-ad-btn').addEventListener('click', () => {
    // Send a request to the bot to process an ad watch
    sendToBot('watch_ad');
    // For simplicity, we close the web app and the bot responds in chat
    Telegram.WebApp.close();
});

document.getElementById('refer-btn').addEventListener('click', () => {
    sendToBot('get_referral_link');
    Telegram.WebApp.close();
});

document.getElementById('bonus-btn').addEventListener('click', () => {
    sendToBot('claim_daily_bonus');
    Telegram.WebApp.close();
});

document.getElementById('withdraw-btn').addEventListener('click', () => {
    sendToBot('start_withdrawal');
    Telegram.WebApp.close();
});

// A function to get the initial user info from the bot
document.addEventListener('DOMContentLoaded', () => {
    sendToBot('get_user_info');
});

// Function to update the UI (this will be used later when we get data from the bot)
function updateUI(data) {
    document.getElementById('user-id').textContent = `ID: ${data.user_id}`;
    document.getElementById('balance').textContent = `BALANCE: ${data.points} POINTS`;
    document.getElementById('daily-watched').textContent = `${data.ads_watched}`;
    // You would also update the progress bar here
}