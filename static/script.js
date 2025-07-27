document.addEventListener('DOMContentLoaded', function () {
        const carousel = document.getElementById('carousel')
        const prevBtn = document.querySelector('.carousel-btn.prev')
        const nextBtn = document.querySelector('.carousel-btn.next')
      
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
      })