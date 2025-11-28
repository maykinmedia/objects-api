function mountSearchHelpToggle() {
    const toggleLink = document.getElementById("toggle-search-help");
    const content = document.getElementById("search-help-content");

    if (!toggleLink || !content) return;

    const showText = toggleLink.dataset.showText;
    const hideText = toggleLink.dataset.hideText;

    toggleLink.addEventListener("click", function (e) {
        e.preventDefault();

        if (content.style.display === "none" || content.style.display === "") {
            content.style.display = "block";
            toggleLink.textContent = hideText;
        } else {
            content.style.display = "none";
            toggleLink.textContent = showText;
        }
    });
}

document.addEventListener("DOMContentLoaded", mountSearchHelpToggle);
