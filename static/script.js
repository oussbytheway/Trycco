document.addEventListener('DOMContentLoaded', function() {
    // Message handling functions
    function closeMessage(messageId) {
        const message = document.getElementById(messageId)
        if (message) {
            message.style.transform = 'translateX(100%)'
            message.style.opacity = '0'
            setTimeout(() => {
                message.remove()
            }, 300)
        }
    }
    
    // Auto-close messages after 8 seconds (success) or 15 seconds (error)
    const messages = document.querySelectorAll('.message')
    messages.forEach((message, index) => {
        const messageId = 'message-' + (index + 1)
        const isError = message.classList.contains('message-error')
        const delay = isError ? 15000 : 8000 // 15s for errors, 8s for success

        // Start progress bar animation
        const progressBar = message.querySelector('.message-progress')
        if (progressBar) {
            progressBar.style.animationDuration = delay + 'ms'
            progressBar.classList.add('animate-progress')
        }

        setTimeout(() => {
            if (document.getElementById(messageId)) {
                closeMessage(messageId)
            }
        }, delay)
    })

    // Carousel functionality for homepage
    const carousel = document.getElementById('carousel')
    const prevBtn = document.querySelector('.carousel-btn.prev')
    const nextBtn = document.querySelector('.carousel-btn.next')
    
    if (carousel && prevBtn && nextBtn) {
        // Calculate scroll amount based on card width and gap
        function getScrollAmount() {
            const card = document.querySelector('.product-card')
            if (!card) return 300
            
            const cardWidth = card.offsetWidth
            const gap = 20 // Gap between cards
            return cardWidth + gap
        }
        
        // Previous button click handler
        prevBtn.addEventListener('click', () => {
            carousel.scrollBy({
                left: -getScrollAmount(),
                behavior: 'smooth'
            })
        })
        
        // Next button click handler
        nextBtn.addEventListener('click', () => {
            carousel.scrollBy({
                left: getScrollAmount(),
                behavior: 'smooth'
            })
        })
        
        // Hide arrows when at the beginning or end of carousel
        function updateArrowVisibility() {
            const scrollPosition = carousel.scrollLeft
            const maxScroll = carousel.scrollWidth - carousel.clientWidth
            
            prevBtn.style.visibility = scrollPosition > 0 ? 'visible' : 'hidden'
            nextBtn.style.visibility = scrollPosition < maxScroll - 5 ? 'visible' : 'hidden'
        }
        
        // Initialize arrow visibility
        updateArrowVisibility()
        
        // Update arrow visibility on scroll
        carousel.addEventListener('scroll', updateArrowVisibility)
        
        // Update on window resize
        window.addEventListener('resize', () => {
            updateArrowVisibility()
        })
    }
    
    // Create image modal if it doesn't exist (for products page)
    function createImageModal() {
        if (document.getElementById('imageModal')) return
        
        const modal = document.createElement('div')
        modal.id = 'imageModal'
        modal.className = 'image-modal'
        modal.innerHTML = `
            <span class="close">&times;</span>
            <img class="modal-content" id="modalImage" />
        `
        
        document.body.appendChild(modal)
        
        // Add click event to close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal()
            }
        })
        
        // Add click event to close button
        const closeBtn = modal.querySelector('.close')
        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal)
        }
    }

    // Search form enhancement (optional - adds live search functionality)
    const searchForm = document.getElementById('searchForm')
    const searchInput = document.getElementById('productSearch')
    
    if (searchInput) {
        let searchTimeout
        
        // Optional: Add live search with debouncing
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim()
            
            // Clear previous timeout
            if (searchTimeout) {
                clearTimeout(searchTimeout)
            }
            
            // Debounce search - automatically submit after user stops typing
            searchTimeout = setTimeout(() => {
                if (searchTerm.length > 2 || searchTerm.length === 0) {
                    console.log('Auto-search for:', searchTerm || '(cleared)')
                    // Uncomment the line below if you want auto-search
                    // searchForm.submit();
                }
            }, 500) // Wait 500ms after user stops typing
        })
        
        // Handle form submission
        searchForm.addEventListener('submit', function(e) {
            // Allow normal form submission - Django will handle it
            console.log('Searching for:', searchInput.value)
        })
    }
    
    // Smooth scroll to top when pagination is used
    const paginationLinks = document.querySelectorAll('.pagination-btn')
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Let the link work normally, but add smooth scroll to top
            setTimeout(() => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                })
            }, 100)
        })
    })
    
    // Loading indicator for form submissions (optional UX enhancement)
    const forms = document.querySelectorAll('form')
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]')
            if (submitBtn) {
                const originalHTML = submitBtn.innerHTML
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'
                submitBtn.disabled = true
                
                // Re-enable after a delay (in case of quick redirects)
                setTimeout(() => {
                    submitBtn.innerHTML = originalHTML
                    submitBtn.disabled = false
                }, 3000)
            }
        })
    })

    // Keyboard navigation for modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal()
        }
    })
})

// Global functions that need to be accessible outside the DOMContentLoaded scope

// Image viewing and downloading functions
function viewImage(imageSrc, productName) {
    // Create modal if it doesn't exist
    if (!document.getElementById('imageModal')) {
        const modal = document.createElement('div')
        modal.id = 'imageModal'
        modal.className = 'image-modal'
        modal.innerHTML = `
            <span class="close">&times;</span>
            <img class="modal-content" id="modalImage" />
        `
        
        document.body.appendChild(modal)
        
        // Add click event to close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal()
            }
        })
        
        // Add click event to close button
        const closeBtn = modal.querySelector('.close')
        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal)
        }
    }

    const modal = document.getElementById('imageModal')
    const modalImg = document.getElementById('modalImage')
    
    // Handle both old and new calling patterns
    if (imageSrc) {
        modal.style.display = 'block'
        modalImg.src = imageSrc
        modalImg.alt = productName || 'Product Image'
    } else {
        // Legacy support: get image from productImage element
        const productImg = document.getElementById('productImage')
        if (productImg) {
            modal.style.display = 'block'
            modalImg.src = productImg.src
        }
    }
}

function closeModal() {
    const modal = document.getElementById('imageModal')
    if (modal) {
        modal.style.display = 'none'
    }
}

function downloadImage() {
    const productImg = document.getElementById('productImage')
    if (productImg) {
        const link = document.createElement('a')
        link.href = productImg.src
        link.download = '{{ product.name|slugify }}.jpg'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }
}

// Quantity functions
function decreaseQuantity() {
    const quantityInput = document.getElementById('quantity')
    if (quantityInput.value > 1) {
        quantityInput.value = parseInt(quantityInput.value) - 1
        updateSummary()
    }
}

function increaseQuantity() {
    const quantityInput = document.getElementById('quantity')
    quantityInput.value = parseInt(quantityInput.value) + 1
    updateSummary()
}

// Color and size selection functions
function selectColor(element) {
    document.querySelectorAll('.color-option').forEach((option) => {
        option.classList.remove('selected')
    })
    element.classList.add('selected')

    const colorSelect = document.getElementById('colorSelect')
    const colorValue = element.getAttribute('data-color')
    colorSelect.value = colorValue
    updateSummary()
}

function selectSize(element) {
    document.querySelectorAll('.size-option').forEach((option) => {
        option.classList.remove('selected')
    })
    element.classList.add('selected')

    const sizeSelect = document.getElementById('sizeSelect')
    const sizeValue = element.getAttribute('data-size')
    sizeSelect.value = sizeValue
    updateSummary()
}

// Update order summary
function updateSummary() {
    const quantity = document.getElementById('quantity').value
    const size = document.getElementById('sizeSelect').value
    const color = document.getElementById('colorSelect').value
    const price = document.getElementById('productPrice').getAttribute('data-price')

    document.getElementById('summaryQuantity').textContent = quantity
    document.getElementById('summarySize').textContent = size
    document.getElementById('summaryColor').textContent = color
    document.getElementById('summaryTotal').textContent = price * quantity + ' DA'
}

// Quick view functionality - Uses viewImage to show image modal
function quickView(productId) {
    console.log('Quick view requested for product:', productId)
    
    // Find the product card
    const productCard = document.querySelector(`[data-product-id="${productId}"]`)
    if (!productCard) {
        console.error('Product card not found for ID:', productId)
        return
    }
    
    // Get the product image and name
    const productImg = productCard.querySelector('.product-image')
    const productName = productCard.querySelector('.product-name')
    
    if (productImg) {
        const imageSrc = productImg.src
        const name = productName ? productName.textContent : 'Product'
        
        // Use the existing viewImage function
        viewImage(imageSrc, name)
    } else {
        console.log('No image found for product:', productId)
    }
}