$(window).on('load', function() {
    const resultToggle = $(".toggle-result");
    const detailToggle = $(".toggle-detail");

    function toggleResult () {
        console.log("toggleresult");
        const result = $(this).siblings('.maintenance-result');
        console.log(result);
        if (result.css('display') == 'none') {
            result.css("display", "block");
        } else {
            result.css("display", "none");
        }
    }

    function toggleDetail () {
        const detail = $(this).siblings('.maintenance-detail');
        if (detail.css('display') == 'none') {
            detail.css("display", "block");
        } else {
            detail.css("display", "none");
        }
    }

    resultToggle.each(function() {
        $(this).on("click", toggleResult)
    });

    detailToggle.each(function() {
        $(this).on("click", toggleDetail);
    });
})
