let blockly_isaac_workspace_url = window.location.origin + "/"

for(let span of document.getElementsByTagName('span')){
    let url = span.getAttribute('b-url')
    if(url == undefined)
        continue
    
    let open_btn = document.createElement('button')
    open_btn.className = 'btn btn-sm btn-success'
    open_btn.innerText = "打开工程"
    open_btn.addEventListener('click',()=>{
        window.open(blockly_isaac_workspace_url + 'index.html?lang=zh-hans&biml_url=' + encodeURIComponent(url))
    })
    span.appendChild(open_btn)

    span.append(' ')

    let a = document.createElement('a')
    a.className = 'btn btn-sm btn-primary'
    a.innerText = "下载工程"
    a.href= blockly_isaac_workspace_url + url
    span.appendChild(a)

    span.appendChild("<br>")
}
