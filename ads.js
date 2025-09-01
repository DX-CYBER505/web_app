const adLink = "https://example.com/adsterra_ad"; // Change this to your actual ad link
const timerDuration = 15; // in seconds

document.getElementById('watchAdBtn').addEventListener('click', () => {
    // Open the ad link in a new tab
    window.open(adLink, '_blank');

    // Hide the 'Watch Ad' button and show the timer
    document.getElementById('watchAdBtn').style.display = 'none';
    const timerElement = document.getElementById('timer');
    timerElement.textContent = `Please wait ${timerDuration} seconds...`;

    let timeRemaining = timerDuration;
    const interval = setInterval(() => {
        timeRemaining--;
        timerElement.textContent = `Please wait ${timeRemaining} seconds...`;
        if (timeRemaining <= 0) {
            clearInterval(interval);
            timerElement.textContent = "Time's up! You can now claim your points.";
            // Show and enable the 'Claim Points' button
            document.getElementById('claimPointsBtn').style.display = 'block';
            document.getElementById('claimPointsBtn').disabled = false;
        }
    }, 1000);
});

document.getElementById('claimPointsBtn').addEventListener('click', () => {
    // Send a message back to the bot
    if (Telegram.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify({ action: 'claim_ad_points' }));
        Telegram.WebApp.close(); // Close the web app after sending the data
    } else {
        alert('Telegram Web App is not available in this context.');
    }
});
