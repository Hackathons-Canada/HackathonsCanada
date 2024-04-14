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

console.log(document.querySelector("button"));
document.querySelector("button").addEventListener("click", function () {
  let usalist1 = document.querySelectorAll(".United");
  usalist1.forEach((ca) => (ca.style.display = "none"));
  let onlinelist1 = document.querySelectorAll(".Online");
  onlinelist1.forEach((ca) => (ca.style.display = "none"));
  let canadalist1 = document.querySelectorAll(".Canada");
  canadalist1.forEach((ca) => (ca.style.display = "block"));
  let otherlist1 = document.querySelectorAll(".other");
  otherlist1.forEach((ca) => (ca.style.display = "none"));
});

document
  .getElementById("nav-contact-tabus")
  .addEventListener("click", function () {
    let canadalist2 = document.querySelectorAll(".Canada");
    canadalist2.forEach((ca) => (ca.style.display = "none"));
    let onlinelist2 = document.querySelectorAll(".Online");
    onlinelist2.forEach((ca) => (ca.style.display = "none"));
    let usalist2 = document.querySelectorAll(".United");
    usalist2.forEach((ca) => (ca.style.display = "block"));
    let otherlist1 = document.querySelectorAll(".other");
    otherlist1.forEach((ca) => (ca.style.display = "none"));
  });

document
  .getElementById("nav-contact-tabon")
  .addEventListener("click", function () {
    let canadalist = document.querySelectorAll(".Canada");
    canadalist.forEach((ca) => (ca.style.display = "none"));
    let usalist = document.querySelectorAll(".United");
    usalist.forEach((ca) => (ca.style.display = "none"));
    let onlinelist = document.querySelectorAll(".Online");
    onlinelist.forEach((ca) => (ca.style.display = "block"));
    let otherlist1 = document.querySelectorAll(".other");
    otherlist1.forEach((ca) => (ca.style.display = "none"));
  });

document
  .getElementById("nav-contact-tabev")
  .addEventListener("click", function () {
    let canadalist = document.querySelectorAll(".Canada");
    canadalist.forEach((ca) => (ca.style.display = "block"));
    let usalist = document.querySelectorAll(".United");
    usalist.forEach((ca) => (ca.style.display = "block"));
    let onlinelist = document.querySelectorAll(".Online");
    onlinelist.forEach((ca) => (ca.style.display = "block"));
    let otherlist1 = document.querySelectorAll(".other");
    otherlist1.forEach((ca) => (ca.style.display = "block"));
  });
