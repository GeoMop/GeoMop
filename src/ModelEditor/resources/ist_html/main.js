// QWebView does not support str.startsWith and str.endsWith
// Workaround for startsWith
if (!String.prototype.startsWith) {
  String.prototype.startsWith = function(searchString, position) {
    position = position || 0;
    return this.indexOf(searchString, position) === position;
  };
}

// Workaround for endsWith
if (!String.prototype.endsWith) {
  String.prototype.endsWith = function(searchString, position) {
      var subjectString = this.toString();
      if (position === undefined || position > subjectString.length) {
        position = subjectString.length;
      }
      position -= searchString.length;
      var lastIndex = subjectString.indexOf(searchString, position);
      return lastIndex !== -1 && lastIndex === position;
  };
}

$(document).ready(function() {
  var latex = $('.md-expression');
  latex.each (function (index, element){
    var code = element.innerHTML;
    if (code.startsWith('{$'))
      code = code.substring(2);

    if (code.endsWith('$}'))
      code = code.substring (0, code.length - 2);

    katex.render (code, element, { displayMode: false });
  });
});