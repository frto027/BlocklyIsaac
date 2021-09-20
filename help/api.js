for(let span of document.getElementsByTagName('span')){
    let url = span.getAttribute('b-url')
    if(url == undefined)
        continue
    
    let open_btn = document.createElement('button')
    open_btn.innerText = "打开工程"
    open_btn.addEventListener('click',()=>{
        window.open('../../index.html?lang=zh-hans&biml_url=' + encodeURIComponent(url))
    })
    span.appendChild(open_btn)

    let a = document.createElement('a')
    a.innerText = "下载文件"
    a.href='../../' + url
    span.appendChild(a)
}
