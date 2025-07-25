window.addEventListener('load', function() {
  setTimeout(function() {
    document.getElementById('loading-overlay').style.display = 'none';
  }, 1000);
});

// Sembunyikan/tampilkan navbar saat scroll
let lastScroll = 0;
const navbar = document.getElementById("navbar");
window.addEventListener("scroll", function () {
  const currentScroll = window.pageYOffset;
  if (currentScroll > lastScroll && currentScroll > 60) {
    // Scroll ke bawah, sembunyikan navbar
    navbar.style.transform = "translateY(-100%)";
  } else {
    // Scroll ke atas, tampilkan navbar
    navbar.style.transform = "translateY(0)";
  }
  lastScroll = currentScroll;
});

// Sidebar toggle
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("mainContent");
const pageWrapper = document.getElementById("pageWrapper");
const sidebarToggle = document.getElementById("sidebarToggle");
let isSidebarOpen = true;

sidebarToggle.addEventListener("click", () => {
  isSidebarOpen = !isSidebarOpen;
  if (isSidebarOpen) {
    sidebar.style.transform = "translateX(0)";
    pageWrapper.classList.remove("justify-center");
    pageWrapper.classList.add("justify-center");
    mainContent.classList.remove("ml-0");
    mainContent.classList.add("ml-64");
  } else {
    sidebar.style.transform = "translateX(-100%)";
    pageWrapper.classList.remove("justify-center");
    pageWrapper.classList.add("justify-center");
    mainContent.classList.remove("ml-64");
    mainContent.classList.add("ml-0");
  }
});

// Set initial state
mainContent.classList.add("ml-64");

const darkModeToggle = document.getElementById("darkModeToggle");
const root = document.documentElement; // <html>

// Load mode from localStorage
if (localStorage.getItem("theme") === "dark") {
  root.classList.add("dark");
}

darkModeToggle.addEventListener("click", () => {
  root.classList.toggle("dark");

  if (root.classList.contains("dark")) {
    localStorage.setItem("theme", "dark");
  } else {
    localStorage.setItem("theme", "light");
  }
});
