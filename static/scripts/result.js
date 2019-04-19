$(window).on('load', function() {
    const detailButtons = $(".toggle-details");

    function toggleDetail () {
        const detail = $(this).siblings('.maintenance-details');
        if (detail.css('display') == 'none') {
            detail.css("display", "block");
        } else {
            detail.css("display", "none");
        }
    }

    detailButtons.each(function() {
        $(this).on("click", toggleDetail);
    });
})
