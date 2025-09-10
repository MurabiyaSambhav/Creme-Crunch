
const slides = document.getElementById('slides');
const dotsContainer = document.getElementById('dots');
const totalSlides = slides.children.length;
let currentIndex = 1;
let slideInterval;

const firstClone = slides.children[0].cloneNode(true);
const lastClone = slides.children[totalSlides - 1].cloneNode(true);

slides.appendChild(firstClone);
slides.insertBefore(lastClone, slides.firstChild);

slides.style.transform = `translateX(${-currentIndex * 100}%)`;

const dots = [];
for (let i = 0; i < totalSlides; i++) {
    const dot = document.createElement('div');
    dot.classList.add('dot');
    dot.addEventListener('click', () => goToSlide(i + 1));
    dotsContainer.appendChild(dot);
    dots.push(dot);
}

function updateSlides() {
    slides.style.transition = 'transform 0.5s ease-in-out';
    slides.style.transform = `translateX(${-currentIndex * 100}%)`;
    dots.forEach(dot => dot.classList.remove('active'));
    let realIndex = currentIndex - 1;
    if (realIndex < 0) realIndex = totalSlides - 1;
    if (realIndex >= totalSlides) realIndex = 0;
    dots[realIndex].classList.add('active');
}

function changeSlide(direction = 1) {
    currentIndex += direction;
    updateSlides();

    if (currentIndex === totalSlides + 1) {
        setTimeout(() => {
            slides.style.transition = 'none';
            currentIndex = 1;
            slides.style.transform = `translateX(${-currentIndex * 100}%)`;
        }, 500);
    }

    if (currentIndex === 0) {
        setTimeout(() => {
            slides.style.transition = 'none';
            currentIndex = totalSlides;
            slides.style.transform = `translateX(${-currentIndex * 100}%)`;
        }, 500);
    }

    resetInterval();
}

function goToSlide(index) {
    currentIndex = index;
    updateSlides();
    resetInterval();
}

function resetInterval() {
    clearInterval(slideInterval);
    slideInterval = setInterval(() => changeSlide(1), 5000);
}

updateSlides();
slideInterval = setInterval(() => changeSlide(1), 5000);

