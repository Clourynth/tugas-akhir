window.addEventListener('load', function() {
  const loadingOverlay = document.getElementById('loading-overlay');
  if (loadingOverlay) {
    setTimeout(function() {
      loadingOverlay.style.display = 'none';
    }, 1000);
  }
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
let isSidebarOpen = false; // Changed to false by default for mobile-first

// Check screen size and set sidebar state on page load
function checkScreenSize() {
  if (window.innerWidth >= 768) { // md breakpoint in Tailwind
    if (!isSidebarOpen) {
      isSidebarOpen = true;
      sidebar.style.transform = "translateX(0)";
      mainContent.style.marginLeft = "16rem"; // 256px = 16rem = ml-64
      pageWrapper.classList.remove("justify-center");
      pageWrapper.classList.add("justify-center");
    }
  } else {
    if (isSidebarOpen) {
      isSidebarOpen = false;
      sidebar.style.transform = "translateX(-100%)";
      mainContent.style.marginLeft = "0";
      pageWrapper.classList.remove("justify-center");
      pageWrapper.classList.add("justify-center");
    }
  }
}

// Initial check
checkScreenSize();

// Check on window resize
window.addEventListener("resize", checkScreenSize);

sidebarToggle.addEventListener("click", () => {
  isSidebarOpen = !isSidebarOpen;
  if (isSidebarOpen) {
    sidebar.style.transform = "translateX(0)";
    if (window.innerWidth >= 768) {
      mainContent.style.marginLeft = "16rem"; // 256px = 16rem = ml-64
      pageWrapper.classList.remove("justify-center");
      pageWrapper.classList.add("justify-center");
    }
  } else {
    sidebar.style.transform = "translateX(-100%)";
    if (window.innerWidth >= 768) {
      mainContent.style.marginLeft = "0";
      pageWrapper.classList.remove("justify-center");
      pageWrapper.classList.add("justify-center");
    }
  }
});

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