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
        // Infinite Scroll State Management
        let isLoading = false;
        let currentPage = 1;
        let hasMoreProducts = true;
        let productsPerPage = 9; // Adjust based on your preference
        let scrollTimeout;
        
        function loadMoreProducts() {
            if (isLoading || !hasMoreProducts) return;
            
            isLoading = true;
            loadingIndicator.style.display = 'block';
            
            console.log(`Loading page ${currentPage + 1}`);
            
            // Make AJAX request to Django backend
            fetch(`/load-more-products/?page=${currentPage + 1}&per_page=${productsPerPage}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.products && data.products.length > 0) {
                    console.log(`Loaded ${data.products.length} products for page ${currentPage + 1}`);
                    
                    // Add new products to grid
                    data.products.forEach(product => {
                        productsGrid.appendChild(createProductCard(product));
                    });
                    
                    currentPage++;
                    
                    // Smooth fade-in animation for new products
                    animateNewProducts(data.products.length);
                } else {
                    console.log('No more products available');
                }
                
                // Use server response to determine if more products exist
                hasMoreProducts = data.has_more || false;
                
                if (!hasMoreProducts) {
                    noMoreProducts.style.display = 'block';
                    console.log('Reached end of products');
                }
                
                loadingIndicator.style.display = 'none';
                isLoading = false;
            })
            .catch(error => {
                console.error('Failed to load products:', error.message);
                
                // Show user-friendly error message
                showErrorMessage();
                
                loadingIndicator.style.display = 'none';
                isLoading = false;
            });
        }
        
        function createProductCard(product) {
            const card = document.createElement('div');
            card.className = 'product-card-listing';
            card.dataset.productId = product.id;
            
            // Handle product image
            const imageHtml = product.picture 
                ? `<img src="${product.picture}" alt="${product.name}" class="product-image">`
                : `<div class="product-image-placeholder"><i class="fas fa-image"></i></div>`;
            
            // Handle colors
            const colorsHtml = product.colors_available && product.colors_available.length > 0
                ? product.colors_available.map(color => `<span class="color-dot" style="background-color: ${color};" title="${color}"></span>`).join('')
                : '';
            
            // Handle sizes
            const sizesHtml = product.sizes_available && product.sizes_available.length > 0
                ? product.sizes_available.map(size => `<span class="size-tag">${size}</span>`).join('')
                : '';
            
            // Handle tags
            const tagsHtml = product.tags && product.tags.length > 0
                ? `<div class="available-tags">${product.tags.map(tag => `<span class="tag-pill">${tag.name}</span>`).join('')}</div>`
                : '';
            
            card.innerHTML = `
                <div class="product-image-container">
                    ${imageHtml}
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
                        <div class="available-colors">${colorsHtml}</div>
                        <div class="available-sizes">${sizesHtml}</div>
                        ${tagsHtml}
                    </div>
                </div>
            `;
            return card;
        }
        
        function animateNewProducts(count) {
            const newCards = productsGrid.querySelectorAll('.product-card-listing:nth-last-child(-n+' + count + ')');
            newCards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 50); // Stagger animation
            });
        }
        
        function showErrorMessage() {
            // Remove any existing error messages
            const existingError = document.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.style.cssText = `
                text-align: center; 
                padding: 20px; 
                margin: 20px 0; 
                background-color: #fee; 
                border: 1px solid #fcc; 
                border-radius: 5px; 
                color: #c33;
            `;
            errorMessage.innerHTML = `
                <p>Failed to load more products. Please try again.</p>
                <button onclick="location.reload()" style="
                    padding: 8px 16px; 
                    background: #007cba; 
                    color: white; 
                    border: none; 
                    border-radius: 4px; 
                    cursor: pointer;
                ">Retry</button>
            `;
            
            productsGrid.parentNode.insertBefore(errorMessage, loadingIndicator);
            
            // Auto-remove error message after 10 seconds
            setTimeout(() => {
                if (errorMessage.parentNode) {
                    errorMessage.remove();
                }
            }, 10000);
        }
        
        function shouldLoadMore() {
            if (isLoading || !hasMoreProducts) return false;
            
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight;
            
            // Load when user is within 300px of bottom
            return scrollTop + windowHeight >= documentHeight - 300;
        }
        
        // Debounced scroll listener for infinite scroll
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            scrollTimeout = setTimeout(() => {
                if (shouldLoadMore()) {
                    loadMoreProducts();
                }
            }, 100); // Debounce by 100ms
        });
        
        // Initialize: Check if we need to load more on page load (in case content doesn't fill screen)
        setTimeout(() => {
            if (shouldLoadMore()) {
                console.log('Initial screen not filled, loading more products');
                loadMoreProducts();
            }
        }, 100);
    }
    
    // Search functionality for products page
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            // Clear previous timeout
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
            
            // Debounce search to avoid excessive API calls
            searchTimeout = setTimeout(() => {
                if (searchTerm.length > 2 || searchTerm.length === 0) {
                    console.log('Search term:', searchTerm || '(cleared)');
                    // Implement search logic here - filter products or make API call
                }
            }, 300);
        });
    }
    
    // Quick view functionality - works on any page
    document.addEventListener('click', function(e) {
        if (e.target.closest('.quick-view-btn')) {
            const productId = e.target.closest('.quick-view-btn').dataset.productId;
            console.log('Quick view requested for product:', productId);
            // Implement quick view modal or redirect to product detail
        }
    });
});