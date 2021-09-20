let content_biml_url = window.location.search.match(/[?&]biml_url=([^&]*)/)
let biml_file_content = undefined

if(content_biml_url){
    let biml_url = decodeURIComponent(content_biml_url[1])
    if(confirm(translate_str('%{OPEN_BIML_FILE_YES_OR_NO}'))){
        /*

        我们向传入的biml链接发起请求
        这会导致biml文件受到同源策略的影响

        */
        let request = new XMLHttpRequest()
        request.addEventListener('load',function(request){
            biml_file_content = this.responseText
            LoadBimlUrlFile()
        })
        request.open('GET',biml_url)
        request.send()
    }
}



function LoadBimlUrlFile(){
    if(Code.workspace == undefined){
        //load next time
        return
    }
    if(biml_file_content != undefined){
        let text = biml_file_content
        biml_file_content = undefined
        let xml = Blockly.Xml.textToDom(text)
        Code.workspace.clear()
        Code.workspace.clearUndo()
        Blockly.Xml.domToWorkspace(xml, Code.workspace)
    }
}