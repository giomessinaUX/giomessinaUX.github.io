function showParagraph(contentId) {
    // Hide all divs including the default one
    document.querySelectorAll('#content > div').forEach(div => div.classList.add('hidden'));
    
    // Show the selected div
    document.getElementById(contentId).classList.remove('hidden');
}

function resetPage() {
    // Hide all divs
    document.querySelectorAll('#content > div').forEach(div => div.classList.add('hidden'));
    
    // Show the default content
    document.getElementById('content0').classList.remove('hidden');
}