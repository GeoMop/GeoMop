function isFilterOneMode () {
    return $('.btn-filter-one').hasClass('active');
}

function fixSelection () {
    if (isFilterOneMode ()) {

    }
}

$(function() {

    var latex = $('.md-expression');
    latex.each (function (index, element){
      var code = element.innerHTML;
      if (code.startsWith('{$'))
        code = code.substring(2);

      if (code.endsWith('$}'))
        code = code.substring (0, code.length - 2);

      katex.render (code, element, { displayMode: false });
    });

    $('.btn-filter-one').click(function(){
        $(this).toggleClass('active');
    });

    $('.btn-filter').click(function(){
        var isActive = $(this).hasClass('active');
        var type = '.'+$(this).data('type');

        if (!isActive) {
            $(type).removeClass('hidden');
        } else {
            $(type).addClass('hidden');
        }

    });

  $(window).on('hashchange',function(){
    if (isFilterOneMode ()) {
        var hash = document.location.hash;
        var section = $('[data-name=' + hash.slice(1) + ']');
        $('.main-section').addClass ('hidden');
        section.removeClass('hidden');
    }else{
        if (!$('.btn-filter').hasClass('active')) {
            $($('.btn-filter').first()).click();
        }
    }
  });

  $('a[href*=#]:not([href=#])').click(function() {
    var current_hash = this.hash;
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      /*var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
        */


      /*if (target.length) {
        diff = Math.abs($(document).scrollTop() - target.offset().top);
        if (diff > 10000) {
            // no animation
            return true;
        }else {
            time = Math.min (diff / 5, 300);

            $('html,body').animate({
              scrollTop: target.offset().top
            }, time, 'swing', function () {
                // on complete set correct location after animation
                document.location.hash = current_hash;
            });
            return false;
        }
      }*/
    };
  });
});