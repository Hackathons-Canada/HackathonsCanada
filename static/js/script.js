document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".flip-card-inner");
  cards.forEach((card) => {
    card.addEventListener("click", function () {
      card.classList.toggle("is-flipped");
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const radioButtons = document.querySelectorAll(
    '.btn-group input[type="radio"]'
  );
  radioButtons.forEach(function (radioButton) {
    radioButton.addEventListener("change", function () {
      const checkedRadioButton = document.querySelector(
        '.btn-group input[type="radio"]:checked'
      );
      const url = checkedRadioButton.nextElementSibling.dataset.url;
      window.location.href = url;
    });
  });
});

const scrollers = document.querySelectorAll(".scroller");


addAnimation();


function addAnimation() {
  scrollers.forEach((scroller) => {
    scroller.setAttribute("data-animated", true);
    const scrollerInner = scroller.querySelector(".scroller__inner");
    const scrollerContent = Array.from(scrollerInner.children);
    scrollerContent.forEach((item) => {
      const duplicatedItem = item.cloneNode(true);
      duplicatedItem.setAttribute("aria-hidden", true);
      scrollerInner.appendChild(duplicatedItem);
    });
  });
}
