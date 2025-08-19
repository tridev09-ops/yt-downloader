const input = document.querySelector('#url')
const fetchBtn = document.querySelector('#fetch-button')
const extBtn = document.querySelector('#extension-button')
const optionCon = document.querySelector('#option-container')
const titleCon = document.querySelector('.title')
const thumbnailCon = document.querySelector('.thumbnail')
const loaderCon = document.querySelector('#loader-container')

ext = 'mp4'

const fetchFormats = async()=> {
    url = input.value.trim()
    if (!url) {
        alert("Enter url to show options")
        return
    }

    loaderCon.style.display = 'grid'

    let res = await fetch("/fetch", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url,
            ext
        })
    })
    let data = await res.json()
    if (data.error) {
        alert(data.error)
        return
    }

    loaderCon.style.display = 'none'
    thumbnailCon.style.display = 'flex'

    titleCon.textContent = data.title
    thumbnailCon.src = data.thumbnail
    optionCon.innerHTML = ''

    if (ext == 'mp4') {
        data.formats.forEach((d)=> {
            optionCon.innerHTML += `
            <div class="option">
            <span class="quality">${d.quality}p</span>
            <span class="size">${d.size}</span>
            <a class="download" href="/download?url=${url}&quality=${d.quality}&ext=${ext}"><i class="fi fi-sr-down-to-line"></i></a>
            </div>
            `
        })
    } else {
        optionCon.innerHTML += `
        <div class="option">
        <span class="quality">192kbps</span>
        <a class="download" href="/download?url=${url}&quality=1080&ext=${ext}"><i class="fi fi-sr-down-to-line"></a>
        </div>`
    }
}

extBtn.addEventListener('click',
    ()=> {
        ext = ext == 'mp4'?'mp3': 'mp4'
        extBtn.textContent = ext
    })

fetchBtn.addEventListener('click',
    fetchFormats)