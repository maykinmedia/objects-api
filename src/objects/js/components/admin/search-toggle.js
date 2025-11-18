import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";

const SearchHelpToggle = () => {
    useEffect(() => {
        const toggleLink = document.getElementById("toggle-search-help");
        const content = document.getElementById("search-help-content");

        if (!toggleLink || !content) return;

        const handleClick = (e) => {
            e.preventDefault();
            if (content.style.display === "none" || content.style.display === "") {
                content.style.display = "block";
                toggleLink.textContent = "Hide search information";
            } else {
                content.style.display = "none";
                toggleLink.textContent = "Show search information";
            }
        };

        toggleLink.addEventListener("click", handleClick);

        return () => toggleLink.removeEventListener("click", handleClick);
    }, []);

    return null;
};

const mountSearchHelpToggle = () => {
    const node = document.getElementById("search-help-toggle-root");
    if (!node) return;

    const root = createRoot(node);
    root.render(<SearchHelpToggle />);
};

export { mountSearchHelpToggle };
