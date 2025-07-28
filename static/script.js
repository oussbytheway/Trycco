document.addEventListener('DOMContentLoaded', function() {
    // Carousel functionality for homepage
    const carousel = document.getElementById('carousel');
    const prevBtn = document.querySelector('.carousel-btn.prev');
    const nextBtn = document.querySelector('.carousel-btn.next');
    
    if (carousel && prevBtn && nextBtn) {
        // Calculate scroll amount based on card width and gap
        function getScrollAmount() {
            const card = document.querySelector('.product-card');
            if (!card) return 300;
            
            const cardWidth = card.offsetWidth;
            const gap = 20; // Gap between cards
            return cardWidth + gap;
        }
        
        // Previous button click handler
        prevBtn.addEventListener('click', () => {
            carousel.scrollBy({
                left: -getScrollAmount(),
                behavior: 'smooth'
            });
        });
        
        // Next button click handler
        nextBtn.addEventListener('click', () => {
            carousel.scrollBy({
                left: getScrollAmount(),
                behavior: 'smooth'
            });
        });
        
        // Hide arrows when at the beginning or end of carousel
        function updateArrowVisibility() {
            const scrollPosition = carousel.scrollLeft;
            const maxScroll = carousel.scrollWidth - carousel.clientWidth;
            
            prevBtn.style.visibility = scrollPosition > 0 ? 'visible' : 'hidden';
            nextBtn.style.visibility = scrollPosition < maxScroll - 5 ? 'visible' : 'hidden';
        }
        
        // Initialize arrow visibility
        updateArrowVisibility();
        
        // Update arrow visibility on scroll
        carousel.addEventListener('scroll', updateArrowVisibility);
        
        // Update on window resize
        window.addEventListener('resize', () => {
            updateArrowVisibility();
        });
    }
    
    // Quick view functionality - Global function that works for all products
    window.quickView = function(productId) {
        console.log('Quick view requested for product:', productId);
        // Implement your quick view modal logic here
        // For example:
        // openQuickViewModal(productId);
    };
    
    // Search form enhancement (optional - adds live search functionality)
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('productSearch');
    
    if (searchInput) {
        let searchTimeout;
        
        // Optional: Add live search with debouncing
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            // Clear previous timeout
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
            
            // Debounce search - automatically submit after user stops typing
            searchTimeout = setTimeout(() => {
                if (searchTerm.length > 2 || searchTerm.length === 0) {
                    console.log('Auto-search for:', searchTerm || '(cleared)');
                    // Uncomment the line below if you want auto-search
                    // searchForm.submit();
                }
            }, 500); // Wait 500ms after user stops typing
        });
        
        // Handle form submission
        searchForm.addEventListener('submit', function(e) {
            // Allow normal form submission - Django will handle it
            console.log('Searching for:', searchInput.value);
        });
    }
    
    // Smooth scroll to top when pagination is used
    const paginationLinks = document.querySelectorAll('.pagination-btn');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Let the link work normally, but add smooth scroll to top
            setTimeout(() => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }, 100);
        });
    });
    
    // Loading indicator for form submissions (optional UX enhancement)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalHTML = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                submitBtn.disabled = true;
                
                // Re-enable after a delay (in case of quick redirects)
                setTimeout(() => {
                    submitBtn.innerHTML = originalHTML;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });
});