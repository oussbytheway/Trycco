// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    const carousel = document.getElementById('carousel');

    // Search functionality
    function handleSearch() {
        const searchValue = searchInput.value.trim();
        if (searchValue) {
            console.log('Search query:', searchValue);
            // Here you would typically send the search query to your backend
            // For now, we'll just log it to the console
        }
    }

    // Search button click event
    searchBtn.addEventListener('click', handleSearch);

    // Search input enter key event
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // Carousel scroll functionality
    let isScrolling = false;
    let scrollTimeout;

    // Add smooth scrolling with mouse wheel
    carousel.addEventListener('wheel', function(e) {
        e.preventDefault();
        carousel.scrollLeft += e.deltaY;
    });

    // Add touch/drag scrolling for mobile
    let isDown = false;
    let startX;
    let scrollLeft;

    carousel.addEventListener('mousedown', function(e) {
        isDown = true;
        carousel.classList.add('active');
        startX = e.pageX - carousel.offsetLeft;
        scrollLeft = carousel.scrollLeft;
    });

    carousel.addEventListener('mouseleave', function() {
        isDown = false;
        carousel.classList.remove('active');
    });

    carousel.addEventListener('mouseup', function() {
        isDown = false;
        carousel.classList.remove('active');
    });

    carousel.addEventListener('mousemove', function(e) {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - carousel.offsetLeft;
        const walk = (x - startX) * 2;
        carousel.scrollLeft = scrollLeft - walk;
    });

    // Category button interactions
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.textContent;
            console.log('Selected category:', category);
            
            // Remove active class from all buttons
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Here you would typically filter products by category
            // For now, we'll just log the selection
        });
    });

    // Product card interactions
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Product card clicked');
            // Here you would typically navigate to product details
        });
    });

    // See more card interaction
    const seeMoreCard = document.querySelector('.see-more-card');
    if (seeMoreCard) {
        seeMoreCard.addEventListener('click', function() {
            console.log('See more clicked');
            // Here you would typically load more products or navigate to products page
        });
    }

    // Smooth scroll reveal animation (optional enhancement)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe sections for scroll animations
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });

    // Initialize first section as visible
    if (sections.length > 0) {
        sections[0].style.opacity = '1';
        sections[0].style.transform = 'translateY(0)';
    }
});

// Additional utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Responsive carousel adjustment
function adjustCarousel() {
    const carousel = document.getElementById('carousel');
    const cards = carousel.querySelectorAll('.product-card, .see-more-card');
    const containerWidth = carousel.offsetWidth;
    const cardWidth = 220; // 200px + 20px gap
    const visibleCards = Math.floor(containerWidth / cardWidth);
    
    // Add scroll indicators if needed
    if (cards.length > visibleCards) {
        carousel.classList.add('scrollable');
    } else {
        carousel.classList.remove('scrollable');
    }
}

// Call on load and resize
window.addEventListener('load', adjustCarousel);
window.addEventListener('resize', debounce(adjustCarousel, 250));