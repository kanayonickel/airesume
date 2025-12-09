// === Desktop Sidebar collapse ===
document.getElementById('sidebar-toggle').onclick = function () {
  document.getElementById('sidebar').classList.toggle('collapsed');
};

// === Responsive Hamburger/Menu Logic ===
function toggleMenu(showMenu) {
  const layout = document.querySelector('.dashboard-layout');
  if (showMenu) {
    layout.classList.add('show-menu');
    layout.classList.remove('show-content');
  } else {
    layout.classList.remove('show-menu');
    layout.classList.add('show-content');
  }
}

function addMobileMenuBtn() {
  // Remove all previous buttons to avoid duplication on resize
  document.querySelectorAll('.mobile-menu-btn').forEach(btn => btn.remove());
  // Create a floating menu icon (bootstrap icon)
  let btn = document.createElement('button');
  btn.innerHTML = `<i class="bi bi-list"></i>`;
  btn.className = 'mobile-menu-btn';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Open menu');
  btn.style = `
    position: fixed;
    top: 22px; left: 22px;
    z-index: 3000;
    background: var(--primary-blue);
    color: #fff;
    border-radius: 7px;
    border: none;
    padding: 7px 12px;
    font-size: 1.55rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px #1547bb22;
    transition: background .13s;
  `;
  btn.onclick = function () {
    // Toggle: if menu visible, switch to content; otherwise show menu
    const layout = document.querySelector('.dashboard-layout');
    if (layout.classList.contains('show-menu')) {
      toggleMenu(false);
    } else {
      toggleMenu(true);
    }
  };
  document.body.appendChild(btn);
}

function mobileInit() {
  if (window.innerWidth < 900) {
    // Start showing just the sidebar (menu view)
    toggleMenu(true);

    addMobileMenuBtn();

    // Clicking any sidebar link shows ONLY main content (hides sidebar)
    document.querySelectorAll('.sidebar-link').forEach(function(link){
      link.addEventListener('click', function(e){
        e.preventDefault();
        toggleMenu(false);
      });
    });
  } else {
    // On desktop: always show everything
    document.querySelector('.dashboard-layout').classList.remove('show-menu', 'show-content');
    document.querySelectorAll('.mobile-menu-btn').forEach(btn => btn.remove());
  }
}

// Run once, and on resize
window.addEventListener('DOMContentLoaded', mobileInit);
window.addEventListener('resize', function() { setTimeout(mobileInit, 110); });

// === Template click => AI chat open (grid-to-chat swap) ===
document.querySelectorAll('.cv-template-img').forEach(function(img){
  img.addEventListener('click', function(){
    document.getElementById('template-picker').classList.add('d-none');
    document.getElementById('ai-chat').classList.remove('d-none');
    document.getElementById('ai-msg-img').src = img.src;
    document.getElementById('ai-msg-img').alt = img.alt;
  });
});


// Sidebar collapse (desktop)
document.getElementById('sidebar-toggle').onclick = function () {
  document.getElementById('sidebar').classList.toggle('collapsed');
};

// Shows AI chat when template clicked
document.querySelectorAll('.cv-template-img').forEach(function(img){
  img.addEventListener('click', function(){
    document.getElementById('template-picker').classList.add('d-none');
    document.getElementById('ai-chat').classList.remove('d-none');
    document.getElementById('ai-msg-img').src = img.src;
    document.getElementById('ai-msg-img').alt = img.alt;
  });
});

// Responsive helper to set sidebar always collapsed, no extra menu button
function mobileSidebarInit() {
  const sidebar = document.getElementById('sidebar');
  const layout = document.querySelector('.dashboard-layout');
  if (window.innerWidth < 900) {
    sidebar.classList.add('collapsed');
    document.querySelector('.progress-nav').style.display = 'none';
    sidebar.style.display = 'flex';
    document.querySelector('.dash-main').style.width = "calc(100vw - 66px)";
    document.querySelector('.dash-main').style.marginLeft = "66px";
  } else {
    sidebar.classList.remove('collapsed');
    document.querySelector('.progress-nav').style.display = '';
    sidebar.style.display = '';
    document.querySelector('.dash-main').style.width = "";
    document.querySelector('.dash-main').style.marginLeft = "";
  }
}

window.addEventListener('DOMContentLoaded', mobileSidebarInit);
window.addEventListener('resize', function() { setTimeout(mobileSidebarInit, 100); });

