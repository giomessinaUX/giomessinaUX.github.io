function showParagraph(contentId) {
    // Hide all paragraphs including the default one
    document.querySelectorAll('#content > p').forEach(p => p.classList.add('hidden'));
    
    // Show the selected paragraph
    document.getElementById(contentId).classList.remove('hidden');
}

function resetPage() {
    // Hide all paragraphs
    document.querySelectorAll('#content > p').forEach(p => p.classList.add('hidden'));
    
    // Show the default content
    document.getElementById('content0').classList.remove('hidden');
}

// The default content (content0) is visible by default,
// so we don't need to call showParagraph() on page load