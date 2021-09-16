/**
MIT License

Copyright (c) 2020-2021 frto027

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
var electron_inject_init = function(){};
(function(){
    electron = undefined
    try{
        electron = require('electron')
    }catch(e){ }
    if(!electron){
        //we are running in web browser
        return
    }

    //we are running in electron, do more things
    const { assert } = require('console');
    const { shell, ipcRenderer, clipboard, remote } = require('electron')
    const { dialog } = require('electron').remote
    const fs = require('fs')
    const path = require('path')
    const zlib = require('zlib')

    const version = Code.getStringParamFromUrl('version', '')

    //用户点击帮助时打开浏览器，而不是新窗口
    //redefine the show help url to open a real web browser
    Blockly.BlockSvg.prototype.showHelp =function(){
        var a = "function" == typeof this.helpUrl?this.helpUrl():this.helpUrl;
        a && shell.openExternal(a)
    }

    //给Code打补丁，当修改语言时，保存配置文件
    const old_change_language = Code.changeLanguage
    Code.changeLanguage = function(){
        var languageMenu = document.getElementById('languageMenu');
        var newLang = encodeURIComponent(
            languageMenu.options[languageMenu.selectedIndex].value);
        ipcRenderer.invoke('change-language',newLang);
        old_change_language()
    }

    //出于安全考虑，我们不加载第三方js脚本
    Code.importPrettify = function(){}
    //给复制粘贴打补丁，当复制粘贴块时，应该复制到系统剪切板
    CLIPBOARD_PREFIX = 'bcdt'
    CLIPBOARD_TAIL = 'isend'
    Blockly.__defineGetter__('clipboardXml_', function(){
        try{
            var compressed_text_buffer = clipboard.readBuffer('io.github.frto027.blocklyisaac.clip')
            //解压->编码utf8->校验首尾->返回dom
            var text = zlib.inflateSync(compressed_text_buffer).toString('utf-8')
            if(text.startsWith(CLIPBOARD_PREFIX) && text.endsWith(CLIPBOARD_TAIL)){
                text = text.substr(CLIPBOARD_PREFIX.length,text.length - CLIPBOARD_PREFIX.length - CLIPBOARD_TAIL.length)
                return Blockly.Xml.textToDom(text)
            }
        }catch(e){ }
        
        return undefined
    })
    Blockly.__defineSetter__('clipboardXml_',function(clipboardXml){
        //编码text->增加首尾->编码utf-8->压缩
        var text = Blockly.Xml.domToText(clipboardXml)
        text = CLIPBOARD_PREFIX + text + CLIPBOARD_TAIL
        var compressed_text_buffer = zlib.deflateSync(Buffer.from(text,'utf8'))
        clipboard.writeBuffer('io.github.frto027.blocklyisaac.clip',compressed_text_buffer)
    })
    //需要拦截原版的ctrl+v
    let orig_onKyeDown = Blockly.onKeyDown
    Blockly.onKeyDown = function(e){
        if (e.altKey || e.ctrlKey || e.metaKey) {
            if (e.keyCode == Blockly.utils.KeyCodes.V) {
                if(Blockly.clipboardXml_ != undefined){
                    Code.workspace.paste(Blockly.clipboardXml_)
                }
                return
            }
        }

        //ctrl s for save
        if (e.altKey || e.ctrlKey || e.metaKey){
            if (e.keyCode == Blockly.utils.KeyCodes.S){
                ToolButtonOperations.save()
                return
            }
        }

        orig_onKyeDown(e)
    }

    Blockly.alert = text =>{
        new Notification(translate_str('%{BLOCKLY_ISAAC_WORKSPACE}'),{body:text})
    }

    const Dialogs = require('dialogs')
    const dialogs = Dialogs(
        {
            ok:translate_str('%{OK}'),
            cancel:translate_str('%{CANCEL}')
        }
    )
    Blockly.prompt = (a,b,c)=>{
        dialogs.prompt(a,b,c)
    }


    //我们需要一个“假的”文件保存提示，因为保存文件太快了，界面没办法相应
    let title_tip = {
        timeout:0,
        text:""
    }
    function tip_text(text, timems){
        title_tip.text = text
        title_tip.timeout = new Date().getTime() + timems
        updateTitle()
        setTimeout(updateTitle, timems + 200)
    }

    //右键菜单中增加复制和粘贴两个操作


    var FileOpenConfig = {
        currentPath : undefined,
        currentFileRecord : undefined, 
        currentModFolder : undefined
    }

    function updateTitle(){
        var str = translate_str('%{BLOCKLY_ISAAC_WORKSPACE}')
        if(FileOpenConfig.currentPath)
            str += ' - ' + path.basename(FileOpenConfig.currentPath)
        if(new Date().getTime() < title_tip.timeout)
            str += ' - ' + title_tip.text
        str += ' ' + version
        document.title = str 
    }

    //File IO
    function openfile(file){
        try{
            var text = fs.readFileSync(file,{encoding:'utf8'})
            var xml = Blockly.Xml.textToDom(text)
            Code.workspace.clear()
            Code.workspace.clearUndo()
            Blockly.Xml.domToWorkspace(xml,Code.workspace)
            FileOpenConfig.currentPath = file
            FileOpenConfig.currentFileRecord = text
            updateTitle()
        }catch(e){ 
            alert('打开文件失败')
        }
    }

    function save_as_file(){
        var file = dialog.showSaveDialogSync(remote.getCurrentWindow(), {
            defaultPath: FileOpenConfig.currentPath, 
            filters:[
                {name:'Blockly Isaac XML', extensions:['biml']}
            ]
        })
        if(file == undefined)
            return
        var xml = Blockly.Xml.workspaceToDom(Code.workspace)
        var text = Blockly.Xml.domToText(xml)
        try{
            fs.writeFileSync(file,text,{encoding:'utf8'})
            FileOpenConfig.currentPath = file
            FileOpenConfig.currentFileRecord = text
            tip_text('保存中',200)
        }catch(e){ 
            alert('文件写入出错，保存失败')
        }
    }

    function savefile(){
        assert(FileOpenConfig.currentPath)

        var current_old_record = undefined
        //check old file
        //try check old files
        try{
            current_old_record = fs.readFileSync(FileOpenConfig.currentPath, {encoding:'utf8'})
        }catch(e){
            if(confirm('文件不存在，是否继续保存？')==false){
                return;
            }
        }
        if(FileOpenConfig.currentFileRecord != undefined && current_old_record != undefined 
        && current_old_record != FileOpenConfig.currentFileRecord){
            if(confirm('检测到项目文件被其它程序修改，是否继续覆盖保存？')==false){
                return;
            }
        }
        var xml = Blockly.Xml.workspaceToDom(Code.workspace)
        var text = Blockly.Xml.domToText(xml)
        try{
        fs.writeFileSync(FileOpenConfig.currentPath,text,{encoding:'utf8'})
        FileOpenConfig.currentFileRecord = text
        tip_text('保存中',200)
        }catch(e){ 
            alert('文件写入出错，保存失败')
        }
        
    }

    //此函数在inject_init被调用
    electron_inject_init = function(){
        updateTitle()

        //复制按钮
        document.getElementById('copy_to_console').hidden = true
        var copy_to_console_btn = document.getElementById('copy_to_console_electron')
        copy_to_console_btn.hidden = false
        Code.bindClick(copy_to_console_btn,function(){
            let comment_func = Blockly.Block.prototype.getCommentText
            Blockly.Block.prototype.getCommentText = ()=>null
            let txt = Blockly.Lua.workspaceToCode(Code.workspace)
            Blockly.Block.prototype.getCommentText = comment_func
            txt = txt.replaceAll(/\n */g,'\n')
            txt = txt.replaceAll('\n',';')
            txt = 'l ' + txt
            clipboard.writeText(txt)
            tip_text('已复制',2000)
        })

        //另存为按钮
        let save_as_btn = document.getElementById('save_file_as')
        save_as_btn.hidden = false

        //去掉“下载离线版本”的按钮
        document.getElementById('download_offline').hidden = true

        //将所有的文件操作进行封装
        ToolButtonOperations.open = function(){
            if(Code.workspace.getAllBlocks(false).length > 0){
                var xml = Blockly.Xml.workspaceToDom(Code.workspace)
                var text = Blockly.Xml.domToText(xml)
                if(FileOpenConfig.currentPath == undefined || text != FileOpenConfig.currentFileRecord){
                    if(confirm('当前文件未保存，是否继续？') == false){
                        return
                    }
                }
            }

            let file = dialog.showOpenDialogSync(remote.getCurrentWindow(), {
                properties:['openFile'],
                filters:[
                    {name:'Blockly Isaac XML', extensions:['biml']}
                ]
            })
            if(file == undefined || file.length == 0){
                console.log('no file open')
                return
            }
            file = file[0]
            
            openfile(file)
        }

        ToolButtonOperations.save = function(){
            if(FileOpenConfig.currentPath){
                savefile()
            }else{
                save_as_file()
            }
        }

        ToolButtonOperations.save_as = save_as_file

        var new_window_btn = document.getElementById('new_window_button')
        new_window_btn.hidden = false
        Code.bindClick(new_window_btn,function(){
            ipcRenderer.invoke('new-window')
        })
    }
})()

