// Existing toggleParagraph function (unchanged)
function toggleParagraph(contentId) {
    const content = document.getElementById(contentId);
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
    } else {
        content.classList.add('hidden');
    }
}

// Updated spoiler functionality with HTML content
const spoilers = [
    "We're planning to add <strong>interactive 3D models</strong>!",
    "The next version will include <em>voice narration</em>.",
    "Soon, you'll be able to <a href='#'>customize the presentation theme</a>.",
    "We're working on a <span style='color: blue;'>collaborative feature</span> for real-time editing.",
    "Future updates will include <strong>AI-powered</strong> content suggestions. <a href='#'>Learn more</a>."
];

function showSpoiler() {
    const spoilerDiv = document.getElementById('spoilerDiv');
    const spoilerLink = document.getElementById('spoilerLink');

    if (spoilerDiv.classList.contains('hidden')) {
        toggleParagraph('spoilerDiv');
    }

    const randomSpoiler = spoilers[Math.floor(Math.random() * spoilers.length)];
    spoilerDiv.innerHTML = randomSpoiler; // Using innerHTML to render HTML content
    spoilerLink.textContent = 'Try again';
}

// Ensure the DOM is loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    const spoilerLink = document.getElementById('spoilerLink');
    if (spoilerLink) {
        spoilerLink.addEventListener('click', function(e) {
            e.preventDefault();
            showSpoiler();
        });
    }
});