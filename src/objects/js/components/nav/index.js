const navNodes = document.querySelectorAll(".nav");

class TabNav {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        // nodes
        this.node = node;
        this.tabButtons = this.node.querySelectorAll(".nav__item");
        this.tabs = this.node.querySelectorAll(".nav__pane");

        this.setActive(this.tabButtons[0]);

        // events
        this.tabButtons.forEach((tabButton) => {
            tabButton.addEventListener("click", (event) => {
                this.setActive(event.target);
            });
        });
    }

    setActive(tabButton) {
        console.log("tabNode=", tabButton);
        // make inactive all tabs and contents
        this.tabButtons.forEach((btn) => {
            btn.classList.remove("nav__item--active");
        });
        this.tabs.forEach((tab) => {
            tab.classList.remove("nav__pane--active");
        });

        // set active for the current tab and content
        tabButton.classList.add("nav__item--active");
        const id = tabButton.dataset.id;
        const tab = document.getElementById(id);
        tab.classList.add("nav__pane--active");
    }
}

[...navNodes].forEach((node) => new TabNav(node));
