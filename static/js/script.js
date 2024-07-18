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
  // Array of image names
  const imageNames = [
    "uft.png",
    "cal.png",
    "delta.png",
    "form.png",
    "gt.png",
    "har.png",
    "hawk.png",
    "la.png",
    "mit.png",
    "north.png",
    "ryth.png",
    "tree.png",
  ];

  // Function to shuffle array
  function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }

  // Function to populate scroller with shuffled images
  function populateScroller(wrapperId, images) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;

    const fragment = document.createDocumentFragment();
    images.forEach((imageName) => {
      const img = document.createElement("img");
      img.src = `/static/assets/${imageName}`;
      img.className =
        wrapperId === "scrollerWrapperLeft"
        ? "item-scroller-left-layout"
        : "item-scroller-right-layout";
      fragment.appendChild(img);
    });

    wrapper.innerHTML = ""; // Clear existing content
    wrapper.appendChild(fragment);
  }

  // Shuffle the image names array
  const shuffledImages = shuffleArray([...imageNames]);

  // Split the shuffled array into two halves
  const midpoint = Math.ceil(shuffledImages.length / 2);
  const leftImages = shuffledImages.slice(0, midpoint);
  const rightImages = shuffledImages.slice(midpoint);

  // Populate both scrollers
  populateScroller("scrollerWrapperLeft", leftImages);
  populateScroller("scrollerWrapperRight", rightImages);

  // Initialize FullCalendar
  var calendarEl = document.getElementById("calendar");
  if (calendarEl) {
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
    });
    calendar.render();
  }
});
