// console.log("Hello World from script.js!");

// document.addEventListener("DOMContentLoaded", function () {
//   const cards = document.querySelectorAll(".flip-card-inner");
//   cards.forEach((card) => {
//     card.addEventListener("click", function () {
//       card.classList.toggle("is-flipped");
//     });
//   });
// });

document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  if (calendarEl) {
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
    });
    calendar.render();
  }
});
