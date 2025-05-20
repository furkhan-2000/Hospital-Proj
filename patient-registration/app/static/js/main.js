const API_BASE = '/api';

// Patient Form Submission
document.getElementById('patientForm').addEventListener('submit', async e => {
    e.preventDefault();

    const payload = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        date_of_birth: document.getElementById('dob').value,
        sex: document.getElementById('sex').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        description: document.getElementById('description').value
    };

    try {
        const res = await fetch(`${API_BASE}/patients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const body = await res.json();
        if (!res.ok) throw new Error(body.error || JSON.stringify(body));

        document.getElementById('patientForm').reset();
        showToast('Patient registered successfully!', 'success');
    } catch (err) {
        showToast(err.message, 'error');
    }
});

function showToast(msg, type) {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    document.getElementById('toastContainer').appendChild(t);
    setTimeout(() => t.remove(), 5000);
}

// Menu Toggle with Sidebar Navigation
$(document).ready(function () {
    $('.menu-toggle').click(function () {
        $('#sidebar-menu').toggleClass('open');
    });

    // Smooth scrolling for menu links within the sidebar menu
    $('#sidebar-menu a[href^="#"]').click(function (e) {
        e.preventDefault();
        const targetId = $(this).attr('href');
        const targetElement = $(targetId);
        if (targetElement.length) {
            $('html, body').animate({
                scrollTop: targetElement.offset().top
            }, 500);
            $('#sidebar-menu').removeClass('open'); // Close the sidebar menu after clicking
        }
    });
});

// Service Slider
const slides = document.querySelectorAll('.slide');
const nav = document.getElementById('sliderNav');
let sIdx = 0;

slides.forEach((_, i) => {
    const btn = document.createElement('button');
    if (i === 0) btn.classList.add('active');
    btn.addEventListener('click', () => showSlide(i));
    nav.appendChild(btn);
});

function showSlide(i) {
    slides[sIdx].classList.remove('active');
    nav.children[sIdx].classList.remove('active');
    sIdx = i;
    slides[sIdx].classList.add('active');
    nav.children[sIdx].classList.add('active');
}

setInterval(() => showSlide((sIdx + 1) % slides.length), 8000);

// Specialist Slider
const specialistSlides = document.querySelectorAll('.specialist-slide');
let specialistIdx = 0;

function showSpecialistSlide(i) {
    specialistSlides.forEach(slide => {
        slide.classList.remove('active');
        slide.style.opacity = '0';
    });
    specialistIdx = i;
    specialistSlides[specialistIdx].classList.add('active');
    specialistSlides[specialistIdx].style.opacity = '1';
}

setInterval(() => showSpecialistSlide((specialistIdx + 1) % specialistSlides.length), 5000);

// Visual Tour Slider
const tourSlides = document.querySelectorAll('.tour-slide');
let tourIdx = 0;

function showTourSlide(i) {
    tourSlides[tourIdx].classList.remove('active');
    tourIdx = i;
    tourSlides[tourIdx].classList.add('active');
}

setInterval(() => showTourSlide((tourIdx + 1) % tourSlides.length), 3000);
