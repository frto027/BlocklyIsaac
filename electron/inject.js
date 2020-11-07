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

    const { shell, ipcRenderer, clipboard } = require('electron')
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
    //TODO: 剪切板压缩存储
    Blockly.__defineGetter__('clipboardXml_', function(){
        var text = clipboard.readText()
        try{
            text = Buffer.from(text,'base64').toString('utf-8')
            if(text.startsWith(CLIPBOARD_PREFIX) && text.endsWith(CLIPBOARD_TAIL)){
                text = text.substr(CLIPBOARD_PREFIX.length,text.length - CLIPBOARD_PREFIX.length - CLIPBOARD_TAIL.length)
                return Blockly.Xml.textToDom(text)
            }
        }catch(e){ }
        
        return undefined
    })
    Blockly.__defineSetter__('clipboardXml_',function(clipboardXml){
        var text = Blockly.Xml.domToText(clipboardXml)
        text = CLIPBOARD_PREFIX + text + CLIPBOARD_TAIL
        text = Buffer.from(text,'utf-8').toString('base64')
        clipboard.writeText(text)
    })
    //需要拦截原版的ctrl+v
    let orig_onKyeDown = Blockly.onKeyDown
    Blockly.onKeyDown = function(e){
        if (e.altKey || e.ctrlKey || e.metaKey) {
            if (e.keyCode == Blockly.utils.KeyCodes.V) {
                if(Blockly.clipboardXml_ != undefined){
                    Code.workspace.paste(Blockly.clipboardXml_)
                }

                return;
            }
        }

        orig_onKyeDown(e)
    }

    //增加文件保存按钮

    //增加文件打开按钮

    //增加输出main.lua的按钮
})()

