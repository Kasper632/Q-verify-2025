
    let lastMessage = "";

    function showNotification(message) {
        //if (message === lastMessage || !message) return;
        lastMessage = message;

        const toast = document.getElementById('data-toast');
        const msg = document.getElementById('toast-message');
        msg.textContent = message;
        toast.style.setProperty('display', 'block', 'important');
        setTimeout(() => toast.style.display = 'none', 5000);
    }

   function pollLatestMessage() {
    console.log("🔁 Försöker hämta senaste status...");
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            console.log("📦 Svar från API:", data);
            showNotification(data.message.trim());
        })
        .catch(error => console.error("❌ API-fel:", error));
}

    setInterval(pollLatestMessage, 302000);
    pollLatestMessage();
