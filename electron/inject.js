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

    const { shell, ipcRenderer } = require('electron')
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

    //给复制粘贴打补丁，当复制粘贴块时，应该复制到系统剪切板
    //TODO

    //增加文件保存按钮

    //增加文件打开按钮

    //增加输出main.lua的按钮
})()

