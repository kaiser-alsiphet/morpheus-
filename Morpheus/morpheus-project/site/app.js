const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// When shared over Wi-Fi, localhost would point to the visitor's computer.
// Resolve detector links to the machine serving this landing page instead.
$$('a[href="http://localhost:7860"]').forEach((link) => {
  link.href = `http://${window.location.hostname}:7860`;
});

window.addEventListener('load', () => {
  window.setTimeout(() => $('#load')?.classList.add('done'), 450);
});

const heading = $('#h1');
if (heading) {
  heading.innerHTML = heading.textContent.trim().split(/\s+/).map((word, index) =>
    `<span class="word"><b style="transition-delay:${index * 0.06}s">${word}</b></span>`
  ).join(' ');
  window.setTimeout(() => heading.classList.add('in'), 120);
}

let lenis;
if (window.Lenis && !reducedMotion) {
  lenis = new window.Lenis({
    duration: 1.05,
    smoothWheel: true,
    syncTouch: false
  });
  const raf = (time) => {
    lenis.raf(time);
    window.requestAnimationFrame(raf);
  };
  window.requestAnimationFrame(raf);
}

$$('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = $(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    if (lenis) lenis.scrollTo(target);
    else target.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth' });
    $('#nav')?.classList.remove('open');
    $('#nb')?.setAttribute('aria-expanded', 'false');
  });
});

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.14 });

$$('.rv').forEach((element) => {
  if (reducedMotion) element.classList.add('in');
  else revealObserver.observe(element);
});

window.addEventListener('scroll', () => {
  const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
  $('#bar').style.width = `${documentHeight > 0 ? (window.scrollY / documentHeight) * 100 : 0}%`;
}, { passive: true });

const menuButton = $('#nb');
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  $('#nav')?.classList.toggle('open', open);
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    $('#nav')?.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  }
});

const ageCheckbox = $('#ok');
const detectorLink = $('#go');
ageCheckbox?.addEventListener('change', () => {
  detectorLink?.setAttribute('aria-disabled', String(!ageCheckbox.checked));
});
detectorLink?.addEventListener('click', (event) => {
  if (!ageCheckbox?.checked) {
    event.preventDefault();
    ageCheckbox?.focus();
  } else {
    document.body.classList.add('leaving');
  }
});

if (window.matchMedia('(pointer: fine)').matches && !reducedMotion) {
  document.body.classList.add('cc');
  const cursor = $('#cur');
  let x = 0; let y = 0; let targetX = 0; let targetY = 0;
  window.addEventListener('mousemove', (event) => { targetX = event.clientX; targetY = event.clientY; });
  const cursorLoop = () => {
    x += (targetX - x) * 0.14;
    y += (targetY - y) * 0.14;
    cursor.style.transform = `translate(${x}px, ${y}px)`;
    window.requestAnimationFrame(cursorLoop);
  };
  cursorLoop();
  $$('a, button, summary, input').forEach((element) => {
    element.addEventListener('mouseenter', () => cursor.classList.add('h'));
    element.addEventListener('mouseleave', () => cursor.classList.remove('h'));
  });
}

$('#df')?.addEventListener('submit', (event) => {
  event.preventDefault();
  const email = $('#em').value;
  window.location.href = `mailto:contact@example.com?subject=Data%20deletion%20request&body=Please%20delete%20data%20linked%20to%20${encodeURIComponent(email)}.`;
  $('#dm').textContent = 'Your email app should open. Send the message to complete the request.';
});

const cookieBanner = $('#ck');
let cookieChoice = null;
try { cookieChoice = window.localStorage.getItem('cc'); } catch (error) { /* storage may be disabled */ }
if (!cookieChoice && cookieBanner) cookieBanner.hidden = false;
$$('#ck button').forEach((button) => button.addEventListener('click', () => {
  try { window.localStorage.setItem('cc', button.dataset.c); } catch (error) { /* storage may be disabled */ }
  cookieBanner.hidden = true;
}));
