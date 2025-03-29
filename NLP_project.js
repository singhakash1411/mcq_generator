
let mode = document.querySelector('.mode');
let currentMode = "dark"; // By default, the page starts in dark mode

// Apply dark mode by default
document.querySelector("body").style.backgroundColor = "#313237";

mode.addEventListener('click', () => {

    if (currentMode == "dark") {
        currentMode = "light";
        document.querySelector("body").style.backgroundColor = "white";
        document.querySelector("h1").style.color = "black";
        document.querySelector("h2").style.color = "black";
        document.querySelector("p").style.color = "black";
         // Switch to light mode background
       // mode.textContent = "Switch to Dark Mode"; // Update button text
    } else {
        currentMode = "dark";
        document.querySelector("body").style.backgroundColor = "#313237"; // Switch to dark mode background
        //ode.textContent = "Switch to Light Mode"; // Update button text
        document.querySelector("h1").style.color = "white";
        document.querySelector("h2").style.color = "white";
        document.querySelector("p").style.color = "white";
    }

    console.log("Current mode:", currentMode);
});
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const nav = document.querySelector('nav');
    const footer = document.querySelector('footer');
    const sec = document.querySelector('.sec');
    nav.classList.toggle('dark-mode');
    footer.classList.toggle('dark-mode');
    sec.classList.toggle('dark-mode');

    // Save the mode in localStorage
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('darkMode', 'enabled');
    } else {
        localStorage.setItem('darkMode', 'disabled');
    }
}



    
    

