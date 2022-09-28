import { Component } from './components/component';
import { Layout } from './layouts/layout';
import { Page } from './pages/page';

export { Component } from './components/component';
export { Layout } from './layouts/layout';
export { Page } from './pages/page';

console.log("JavaScript is working!");
console.log(Component);
console.log(Layout);
console.log(Page);


// Old JS, needs updating
function changeStreakValueDisplay() {
  var streak_elms = document.querySelectorAll('.streak-value');
  if (streak_elms !== undefined) {
    for (var i = 0; i < streak_elms.length; i++) {
      let old_html = streak_elms[i].innerHTML;
      let new_html;
      if (Number(old_html) > 0) {
        new_html = "W" + old_html;
      } else if (Number(old_html) < 0) {
        new_html = "L" + Math.abs(old_html);
      } else {
        new_html = "T" + old_html;
      }
      streak_elms[i].innerHTML = new_html;
    }
  }
}

// window.addEventListener("load", changeStreakValueDisplay);
changeStreakValueDisplay();