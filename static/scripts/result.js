$(window).on('load', function() {
    const toggle = $(".toggle");

    function toggleDetails () {
        const targetName = $(this).attr('target');
        const targets = $('.' + targetName);
        targets.each(function() {
            if ($(this).css('display') == 'none') {
                $(this).css("display", "table-row");
            } else {
                $(this).css("display", "none");
            }
        })
    }

    toggle.each(function() {
        $(this).on("click", toggleDetails)
    });

})
