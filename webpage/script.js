/* =========================================
   Glint Landing Page — JavaScript
   Scroll reveals, typing effect, nav scroll,
   and copy-to-clipboard.
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {

    // --- Scroll Reveal (Intersection Observer) ---
    const revealElements = document.querySelectorAll('.reveal');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.dataset.delay || 0);
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, delay);
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(el => revealObserver.observe(el));

    // --- Nav Scroll Effect ---
    const nav = document.getElementById('nav');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;
        if (scrollY > 40) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
        lastScroll = scrollY;
    }, { passive: true });

    // --- Typing Effect for Mica Demo ---
    const typedEl = document.querySelector('.mica-typed');
    const phrases = [
        'Make this sound more professional.',
        'Translate this to Spanish.',
        'Rewrite for a Twitter post.',
        'Simplify this for a 5-year-old.',
        'Add more technical detail.'
    ];
    let phraseIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typeDelay = 60;

    function typeLoop() {
        if (!typedEl) return;

        const currentPhrase = phrases[phraseIndex];

        if (!isDeleting) {
            typedEl.textContent = currentPhrase.substring(0, charIndex + 1);
            charIndex++;

            if (charIndex === currentPhrase.length) {
                isDeleting = true;
                typeDelay = 2000; // Pause before deleting
            } else {
                typeDelay = 50 + Math.random() * 40;
            }
        } else {
            typedEl.textContent = currentPhrase.substring(0, charIndex - 1);
            charIndex--;

            if (charIndex === 0) {
                isDeleting = false;
                phraseIndex = (phraseIndex + 1) % phrases.length;
                typeDelay = 400; // Pause before next phrase
            } else {
                typeDelay = 25;
            }
        }

        setTimeout(typeLoop, typeDelay);
    }

    // Start typing after a delay
    setTimeout(typeLoop, 1500);

    // --- Copy to Clipboard ---
    const copyBtn = document.getElementById('copyBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const code = copyBtn.previousElementSibling.textContent;
            navigator.clipboard.writeText(code).then(() => {
                copyBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
                copyBtn.style.color = '#22c55e';
                setTimeout(() => {
                    copyBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>';
                    copyBtn.style.color = '';
                }, 2000);
            });
        });
    }

    // --- Smooth Scroll for anchor links ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const href = anchor.getAttribute('href');
            if (href === '#') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

});
