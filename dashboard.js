// Function to send data back to the bot
function sendToBot(action, data = {}) {
    if (Telegram.WebApp) {
        const payload = { action, ...data };
        Telegram.WebApp.sendData(JSON.stringify(payload));
    }
}

// Handle button clicks
document.getElementById('adsBtn').addEventListener('click', () => {
    // For ads, we can still open an external link
    const adLink = "https://example.com/adsterra_ad"; // Change to your ad link
    window.open(adLink, '_blank');
    alert("Ad opened in a new tab. After watching, please wait for the points to be credited.");
    // In a more advanced version, we would verify the ad view before awarding points.
});

document.getElementById('dailyBonusBtn').addEventListener('click', () => {
    sendToBot('claim_daily_bonus');
    Telegram.WebApp.close();
});

document.getElementById('referBtn').addEventListener('click', () => {
    sendToBot('get_referral_link');
    Telegram.WebApp.close();
});

document.getElementById('withdrawBtn').addEventListener('click', () => {
    sendToBot('start_withdrawal');
    Telegram.WebApp.close();
});

// Request initial data from the bot
document.addEventListener('DOMContentLoaded', () => {
    sendToBot('get_user_info');
});