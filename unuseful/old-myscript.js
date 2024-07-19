function showParagraph(contentId) {
    // Hide all divs including the default one
    document.querySelectorAll('#content > div').forEach(div => div.classList.add('hidden'));
    
    // Show the selected div
    document.getElementById(contentId).classList.remove('hidden');
}
function showParagraph(contentId) {
    // Hide all divs including the default one
    document.querySelectorAll('#chance > div').forEach(div => div.classList.add('hidden'));
    
    // Show the selected div
    document.getElementById(contentId).classList.remove('hidden');
}

function resetPage() {
    // Hide all divs in content
    document.querySelectorAll('#content > div').forEach(div => div.classList.add('hidden'));
       
}
function resetPage1() {
 
         // Hide all divs in chance
     document.querySelectorAll('#chance > div').forEach(div => div.classList.add('hidden'));
    
}
