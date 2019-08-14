const container = document.querySelector('.container')
const pass = document.querySelector('.pass')
const nets = document.querySelectorAll('.name')
const wifi = document.querySelector('#wifi')
let wifiName = ''
let password = ''
container.addEventListener('click' , (e) => {
    if (e.target.className === 'name') {
        for (let net of nets) {
            net.style.fontWeight = 'normal'
        }
        e.target.style.fontWeight = "bold"
        wifiName = e.target.innerText
        pass.style.visibility = 'visible'
        pass.style.opacity = 1
        wifi.value = wifiName
        console.log(wifiName)

        
    }
})

