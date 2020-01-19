/* 1. TOGGLE SIDEBAR
--------------------------------------------------------- */
$("#sidebar-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
});

/* 2. COLLAPSE LINKS IN SIDEBAR
--------------------------------------------------------- */
$('.sidebar-nav li a').click(function(e)
{
    if($('li:hidden', $(this).next()).length)
    {
        e.preventDefault();
        $('.sidebar-nav li ul.in').collapse('hide');
        $(this).next('ul').collapse('show');
    }
    else if($('li:visible', $(this).next()).length)
    {
        e.preventDefault();
    	$(this).next('ul').collapse('hide');
    }
});
$('.sidebar-nav li.active ul').addClass('in');

/* 3. CONFIRM BOX
--------------------------------------------------------- */
$(document).on('click touchstart', '[data-confirm]:not(.disabled):not([disabled])', function(evt)
{
    evt.preventDefault();
    var text = $(this).attr('data-confirm');
    var source = $(this);

    bootbox.confirm({
        message: text,
        callback: function(result) {
            if(result)
            {
                if(source.is('[type="submit"]'))
                {
                    $(document).off('click touchstart', '[data-confirm]:not(.disabled):not([disabled])');
                    source.click();
                }
                else if(source.is('a'))
                {
                    $(location).attr('href', source.attr('href'));
                }
            }
        }
    });
});

/* 4. TOOLTIP ACTIVATION
--------------------------------------------------------- */
$(function () {
    $("[data-toggle='tooltip']").tooltip();
    $("[data-toggle='popover']").popover();
});

/* 5. NOTIFICATION
--------------------------------------------------------- */
$(function () {
	if($('#notify').length)
    {
		$('#notify').slideDown(500);
        if($( window ).width() < 768)
            $('#content-wrapper').animate({'top' : '+=46'}, 500);

		setTimeout(function() {
			$('#notify').slideUp(500);
            if($( window ).width() < 768)
                $('#content-wrapper').animate({'top' : '-=46'}, 500);
		}, 8000);
	}
});


/* 7. TINYNAV
--------------------------------------------------------- */
$(function () {
    $('.panel-heading .nav-tabs').tinyNav({
        active: 'active'
    });
});
