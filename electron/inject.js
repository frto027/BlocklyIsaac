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

    const { shell, ipcRenderer, clipboard } = require('electron')
    const zlib = require('zlib')

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
        var compressed_text_buffer = zlib.deflateSync(Buffer.from(text,'utf-8'))
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

                return;
            }
        }

        orig_onKyeDown(e)
    }


    //右键菜单中增加复制和粘贴两个操作

    //此函数在inject_init被调用
    electron_inject_init = function(){
        //另存为按钮
        //TODO
        //将所有的按钮移动到菜单中
    }

    //增加输出main.lua的按钮
})()

