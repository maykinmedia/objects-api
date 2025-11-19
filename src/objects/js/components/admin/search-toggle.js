function mountSearchHelpToggle() {
    const toggleLink = document.getElementById("toggle-search-help");
    const content = document.getElementById("search-help-content");

    if (!toggleLink || !content) return;

    toggleLink.addEventListener("click", function (e) {
        e.preventDefault();

        if (content.style.display === "none" || content.style.display === "") {
            content.style.display = "block";
            toggleLink.textContent = "Hide search information";
        } else {
            content.style.display = "none";
            toggleLink.textContent = "Show search information";
        }
    });
}

document.addEventListener("DOMContentLoaded", mountSearchHelpToggle);
