const flipCardWrapAll = document.querySelector("#flip-card-wrap-all")
const cardsWrapper = document.querySelectorAll(".flip-card-3D-wrapper")
const cards = document.querySelectorAll(".flip-card")
let frontButtons = ""
let backButtons = ""

for (let i = 0; i < cardsWrapper.length; i++) {
frontButtons = cardsWrapper[i].querySelector(".flip-card-btn-turn-to-back")
frontButtons.style.visibility = "visible"
frontButtons.onclick = function() {
cards[i].classList.toggle('do-flip')
}
  
backButtons = cardsWrapper[i].querySelector(".flip-card-btn-turn-to-front")
backButtons.style.visibility = "visible"
backButtons.onclick = function() {
cards[i].classList.toggle('do-flip')
 }  
} 