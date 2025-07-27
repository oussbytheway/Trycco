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
    
    // Products page functionality
    const loadingIndicator = document.getElementById('loadingIndicator');
    const noMoreProducts = document.getElementById('noMoreProducts');
    const productsGrid = document.getElementById('productsGrid');
    const searchInput = document.getElementById('productSearch');
    
    if (productsGrid) {
        // Infinite Scroll Implementation
        let isLoading = false;
        let currentPage = 1;
        let hasMoreProducts = true;
        
        function loadMoreProducts() {
            if (isLoading || !hasMoreProducts) return;
            
            isLoading = true;
            loadingIndicator.style.display = 'block';
            
            // Simulate API call - replace with actual Django endpoint
            setTimeout(() => {
                // Simulate end of products after 3 pages
                if (currentPage >= 3) {
                    hasMoreProducts = false;
                    loadingIndicator.style.display = 'none';
                    noMoreProducts.style.display = 'block';
                } else {
                    // Add mock products (replace with actual data from Django)
                    const mockProducts = generateMockProducts(6);
                    mockProducts.forEach(product => {
                        productsGrid.appendChild(createProductCard(product));
                    });
                    currentPage++;
                    loadingIndicator.style.display = 'none';
                }
                isLoading = false;
            }, 1000);
        }
        
        function createProductCard(product) {
            const card = document.createElement('div');
            card.className = 'product-card-listing';
            card.innerHTML = `
                <div class="product-image-container">
                    <div class="product-image-placeholder">
                        <i class="fas fa-image"></i>
                    </div>
                    <div class="product-overlay">
                        <button class="quick-view-btn" data-product-id="${product.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-price">${product.price} DA</p>
                    <div class="product-options">
                        <div class="available-colors">
                            ${product.colors.map(color => `<span class="color-dot" style="background-color: ${color};" title="${color}"></span>`).join('')}
                        </div>
                        <div class="available-sizes">
                            ${product.sizes.map(size => `<span class="size-tag">${size}</span>`).join('')}
                        </div>
                    </div>
                </div>
            `;
            return card;
        }
        
        function generateMockProducts(count) {
            const products = [];
            const names = ['Urban Tee', 'Street Style', 'Classic Fit', 'Modern Cut', 'Retro Vibe', 'Minimalist'];
            const colors = ['#000000', '#ffffff'];
            const sizes = ['S', 'M', 'L', 'XL'];
            
            for (let i = 0; i < count; i++) {
                products.push({
                    id: Date.now() + i,
                    name: names[Math.floor(Math.random() * names.length)],
                    price: Math.floor(Math.random() * 5000) + 1000,
                    colors: [colors[Math.floor(Math.random() * colors.length)]],
                    sizes: sizes.slice(0, Math.floor(Math.random() * 3) + 1)
                });
            }
            return products;
        }
        
        // Scroll listener for infinite scroll
        window.addEventListener('scroll', () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                loadMoreProducts();
            }
        });
    }
    
    // Search functionality for products page
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            // Implement search logic here - filter products or make API call
            console.log('Searching for:', searchTerm);
        });
    }
    
    // Quick view functionality - works on any page
    document.addEventListener('click', function(e) {
        if (e.target.closest('.quick-view-btn')) {
            const productId = e.target.closest('.quick-view-btn').dataset.productId;
            // Implement quick view modal or redirect to product detail
            console.log('Quick view product:', productId);
        }
    });
});