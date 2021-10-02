// Test JavaScript
console.log('JavaScript here!');

// window.setTimeout(function() {
//   $(".alert").fadeTo(500, 0).slideUp(500, function(){
//       $(this).remove(); 
//   });
// }, 2000);


function changeStreakValueDisplay() {
  var streak_elms = document.querySelectorAll('.streak-value');
  for (var i = 0; i < streak_elms.length; i++) {
    old_html = streak_elms[i].innerHTML
    if (Number(old_html) > 0) {
      new_html = "W" + old_html;
    } else if (Number(old_html) < 0) {
      new_html = "L" + Math.abs(old_html);
    } else {
      new_html = "T"
    }
    streak_elms[i].innerHTML = new_html;
  }
}

window.addEventListener("load", changeStreakValueDisplay);