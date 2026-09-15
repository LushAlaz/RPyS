function convertOptionToString(option) {
    switch (option) {
        case 0:
            return "rock"
            break;
        case 1:
            return "paper"
            break;
        case 2:
            return "scissors"
            break;
        default:
            return "Unknown"
            break;
    }
}
function pickRandomAndCompare(playerOption, computerOption) {
    // theres prolly a better way to do this
    // but i dont care enough for now
    switch (playerOption) {
        case 0:
            switch (computerOption) {
                case 0:
                    return -1
                case 1:
                    return 0
                case 2:
                    return 1
                default:
                    return null
            }
            break;
        case 1:
            switch (computerOption) {
                case 0:
                    return 1
                case 1:
                    return -1
                case 2:
                    return 0
                default:
                    return null
            }
            break;
        case 2:
            switch (computerOption) {
                case 0:
                    return 0
                case 1:
                    return 1
                case 2:
                    return -1
                default:
                    return null
            }
            break;
        default:
            return -Infinity
            break;
    }
}
async function sendWin() {
    let response = await fetch("/win", { method: "POST" })
    if (!response.ok) {
        statusFlash.style.color = "red"
        statusFlash.innerText = await response.text()
        return
    }

    let winCount = await response.text()
    statusFlash.style.color = "black"
    statusFlash.innerText = `The computer picked ${computerOption}, you win!\nYou now have ${winCount} wins.`
}
function onButtonClick(playerOption) {
    computerOption = Math.floor(Math.random() * 3)
    result = pickRandomAndCompare(playerOption, computerOption)
    console.log(arguments)
    computerOption = convertOptionToString(computerOption)
    if (result == 1) {
        sendWin()
    }
    else if (result == 0) {
        statusFlash.style.color = "black"
        statusFlash.innerText = `The computer picked ${computerOption}, you lose!`
    }
    else {
        statusFlash.style.color = "black"
        statusFlash.innerText = `The computer picked ${computerOption}, game tied!`
    }
}

const rockButton = document.getElementById("rock")
const paperButton = document.getElementById("paper")
const scissorsButton = document.getElementById("scissors")

const statusFlash = document.getElementById("flash")

rockButton.addEventListener("click", () => onButtonClick(0))
paperButton.addEventListener("click", () => onButtonClick(1))
scissorsButton.addEventListener("click", () => onButtonClick(2))