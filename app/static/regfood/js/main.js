$(function () {
    "use strict";

    //======menu fix js======
    var navoff = $('.main_menu').offset().top;
    $(window).scroll(function () {
        var scrolling = $(this).scrollTop();

        if (scrolling > navoff) {
            $('.main_menu').addClass('menu_fix');
        } else {
            $('.main_menu').removeClass('menu_fix');
        }
    });
    //=========NICE SELECT=========
    $('.select_js').niceSelect();


    //=======OFFER ITEM SLIDER======
    $('.offer_item_slider').slick({
        slidesToShow: 3,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 4000,
        dots: false,
        arrows: true,
        nextArrow: '<i class="far fa-long-arrow-right nextArrow"></i>',
        prevArrow: '<i class="far fa-long-arrow-left prevArrow"></i>',
        responsive: [
            {
                breakpoint: 1400,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 1,
                }
            },
            {
                breakpoint: 576,
                settings: {
                    arrows: false,
                    slidesToShow: 1,
                }
            }
        ]
    });


    //*==========ISOTOPE==============
    var $grid = $('.grid').isotope({});

    $('.menu_filter').on('click', 'button', function () {
        var filterValue = $(this).attr('data-filter');
        $grid.isotope({
            filter: filterValue
        });
    });

    //active class
    $('.menu_filter button').on("click", function (event) {

        $(this).siblings('.active').removeClass('active');
        $(this).addClass('active');
        event.preventDefault();
    });


    //=======TEAM SLIDER======
    $('.team_slider').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 4000,
        dots: false,
        arrows: true,
        nextArrow: '<i class="far fa-long-arrow-right nextArrow"></i>',
        prevArrow: '<i class="far fa-long-arrow-left prevArrow"></i>',
        responsive: [
            {
                breakpoint: 1400,
                settings: {
                    slidesToShow: 3,
                }
            },
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 3,
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 576,
                settings: {
                    arrows: false,
                    slidesToShow: 1,
                }
            }
        ]
    });


    //=======DOWNLOAD SLIDER======
    $('.download_slider_item').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 3000,
        dots: false,
        arrows: false,

        responsive: [
            {
                breakpoint: 1400,
                settings: {
                    slidesToShow: 3,
                }
            },
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 3,
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 576,
                settings: {
                    slidesToShow: 1,
                }
            }
        ]
    });


    //=======COUNTER JS=======
    $('.counter').countUp();


    //=======OFFER ITEM SLIDER======
    $('.testi_slider').slick({
        slidesToShow: 2,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 4000,
        dots: false,
        arrows: true,
        nextArrow: '<i class="far fa-long-arrow-right nextArrow"></i>',
        prevArrow: '<i class="far fa-long-arrow-left prevArrow"></i>',
        responsive: [
            {
                breakpoint: 1400,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 1,
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 1,
                }
            },
            {
                breakpoint: 576,
                settings: {
                    arrows: false,
                    slidesToShow: 1,
                }
            }
        ]
    });


    //=======BRAND SLIDER======
    $('.blog_slider').slick({
        slidesToShow: 3,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 4000,
        dots: false,
        arrows: true,
        nextArrow: '<i class="far fa-long-arrow-right nextArrow"></i>',
        prevArrow: '<i class="far fa-long-arrow-left prevArrow"></i>',

        responsive: [
            {
                breakpoint: 1400,
                settings: {
                    slidesToShow: 3,
                }
            },
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 1,
                }
            },
            {
                breakpoint: 576,
                settings: {
                    arrows: false,
                    slidesToShow: 1,
                }
            }
        ]
    });


    //*=======SCROLL BUTTON=======
    $('.scroll_btn').on('click', function () {
        $('html, body').animate({
            scrollTop: 0,
        }, 300);
    });

    $(window).on('scroll', function () {
        var scrolling = $(this).scrollTop();

        if (scrolling > 500) {
            $('.scroll_btn').fadeIn();
        } else {
            $('.scroll_btn').fadeOut();
        }
    });


    //======= VENOBOX.JS.=========
    $('.venobox').venobox();


    //*========STICKY SIDEBAR=======
    $("#sticky_sidebar").stickit({
        top: 10,
    })


    //=======OFFER ITEM SLIDER======
    $('.related_product_slider').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 4000,
        dots: false,
        arrows: true,
        nextArrow: '<i class="far fa-long-arrow-right nextArrow"></i>',
        prevArrow: '<i class="far fa-long-arrow-left prevArrow"></i>',

        responsive: [
            {
                breakpoint: 1400,
                settings: {
                    slidesToShow: 4,
                }
            },
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 3,
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 576,
                settings: {
                    arrows: false,
                    slidesToShow: 1,
                }
            }
        ]
    });


    //======wow js=======
    new WOW().init();


    //=======PRODUCT DETAILS SLIDER======
    if ($("#exzoom").length > 0) {
        $("#exzoom").exzoom({
            autoPlay: true,
        });
    }

    //=======SMALL DEVICE MENU ICON======
    $(".navbar-toggler").on("click", function () {
        $(".navbar-toggler").toggleClass("show");
    });

    // ====== DASHBOARD AJAX NAVIGATION ====== 
    $(document).on('click', '.ajax-link', function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        if (!href || href === '#' || href === 'javascript:void(0);') return;

        // Update active class immediately
        $('.dashboard_menu ul li a').removeClass('active');
        $(this).addClass('active');

        // Visual feedback
        $('.dashboard_content').css('opacity', '0.5').css('pointer-events', 'none');
        $('html, body').animate({ scrollTop: $('.dashboard_area').offset().top - 100 }, 300);

        // Fetch new content
        $.ajax({
            url: href,
            method: 'GET',
            success: function(response) {
                // Parse response to find the dashboard_content div
                var parsed = $($.parseHTML(response));
                var newContent = parsed.find('.dashboard_content').html();
                
                if (newContent) {
                    $('.dashboard_content').html(newContent).css('opacity', '1').css('pointer-events', 'auto');
                    // Re-initialize scripts needed for the new content
                    if ($('.select_js').length) {
                        $('.select_js').niceSelect();
                    }
                    
                    // Update history
                    history.pushState(null, '', href);
                } else {
                    // Fallback if structure changes
                    window.location.href = href;
                }
            },
            error: function() {
                // Fallback
                window.location.href = href; 
            }
        });
    });

    // Handle back/forward buttons for Dashboard
    window.addEventListener('popstate', function(e) {
        var path = window.location.pathname;
        if (path.includes('/profile') || 
            path.includes('/my-orders') || 
            path.includes('/order/') ||
            path.includes('/wishlist') ||
            path.includes('/owner/dishes') ||
            path.includes('/owner/orders') ||
            path.includes('/owner/coupons') ||
            path.includes('/change-password')) {
            
            $('.dashboard_content').css('opacity', '0.5').css('pointer-events', 'none');
            $.ajax({
                url: window.location.href,
                method: 'GET',
                success: function(response) {
                    var parsed = $($.parseHTML(response));
                    var newContent = parsed.find('.dashboard_content').html();
                    if (newContent) {
                        $('.dashboard_content').html(newContent).css('opacity', '1').css('pointer-events', 'auto');
                        // update active link
                        $('.dashboard_menu ul li a').removeClass('active');
                        $('.dashboard_menu ul li a[href="'+path+'"]').addClass('active');
                        if ($('.select_js').length) {
                            $('.select_js').niceSelect();
                        }
                    } else {
                        window.location.reload();
                    }
                },
                error: function() { window.location.reload(); }
            });
        }
    });

    // ====== CART AJAX ADD ======
    $(document).on('submit', 'form[action*="/cart/add/"]', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var formData = form.serialize();

        $.ajax({
            type: "POST",
            url: url,
            data: formData,
            headers: { 'Accept': 'application/json' },
            success: function(response) {
                if (response.success) {
                    // Update cart count in header
                    $('#cart_count, .cart_icon span').text(response.count);
                    
                    // Success Notification
                    var toast = $('<div class="alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3 shadow" style="z-index: 9999;"><i class="fas fa-shopping-basket me-2"></i>' + response.message + '</div>');
                    $('body').append(toast);
                    setTimeout(function() { toast.fadeOut(function() { $(this).remove(); }); }, 3000);
                }
            },
            error: function() {
                alert('Something went wrong. Please try again.');
            }
        });
    });

    // ====== WISHLIST AJAX TOGGLE ======
    $(document).on('submit', 'form[action*="/wishlist/add/"], form[action*="/wishlist/remove/"]', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var formData = form.serialize();
        var isRemove = url.indexOf('/remove/') !== -1;
        
        // Find potential heart icons to update (overlay, in-card, or standalone button)
        var heartIcon = form.find('.fa-heart');
        if (!heartIcon.length) heartIcon = form.closest('.menu_item').find('.fa-heart');
        if (!heartIcon.length) heartIcon = form.parent().find('.fa-heart');
        
        $.ajax({
            type: "POST",
            url: url,
            data: formData,
            headers: { 'Accept': 'application/json' },
            success: function(response) {
                if (response.success) {
                    // Toggle icon state visually
                    if (isRemove) {
                        heartIcon.removeClass('fas text-danger').addClass('fal');
                        // Special handling for the Wishlist Page (remove the card)
                        if (window.location.pathname.includes('/wishlist')) {
                            form.closest('.col-xxl-4, .col-md-6, .col-xl-4').fadeOut(function() {
                                $(this).remove();
                                if ($('.menu_item').length === 0) {
                                    location.reload(); // Reload to show empty state illustration
                                }
                            });
                        }
                        // Update form action/button if it's a toggle (on details page for example)
                        var newUrl = url.replace('/remove/', '/add/');
                        form.attr('action', newUrl);
                    } else {
                        heartIcon.removeClass('fal').addClass('fas text-danger');
                        var newUrl = url.replace('/add/', '/remove/');
                        form.attr('action', newUrl);
                    }

                    // Notification Toast
                    var toastClass = isRemove ? 'alert-info' : 'alert-success';
                    var icon = isRemove ? 'fas fa-heart-broken' : 'fas fa-heart';
                    var toast = $('<div class="alert ' + toastClass + ' position-fixed top-0 start-50 translate-middle-x mt-3 shadow" style="z-index: 9999;"><i class="' + icon + ' me-2"></i>' + response.message + '</div>');
                    $('body').append(toast);
                    setTimeout(function() { toast.fadeOut(function() { $(this).remove(); }); }, 3000);
                }
            },
            error: function() {
                // If not logged in, the server might redirect to login (302), which AJAX handles as error or follows
                // Usually better to redirect manually if we get a 401 or similar
                window.location.reload(); 
            }
        });
    });

});
