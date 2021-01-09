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

const { app, BrowserWindow, ipcMain } = require("electron")
const fs = require("fs")
const { url } = require("inspector")
const path = require("path")
const assert = require("assert")

if(!app.requestSingleInstanceLock()){
  app.quit()
}

const is_dev = process.argv.indexOf('--dev') != -1 || process.argv.indexOf('-d') != -1

const config_file = path.join(app.getPath('userData'), 'blockly_config.json')

console.log(`config file path:${config_file}`)

//default config
app_config = {
  defaultLanguage:'en'
}
if(fs.existsSync(config_file)){
  try{
    app_config = JSON.parse(fs.readFileSync(config_file,{encoding:'utf-8'}))
  }catch(e){ }
}

function write_config(key,value){
  app_config[key]=value
  fs.writeFileSync(config_file,JSON.stringify(app_config),{encoding:'utf-8'})
}

function read_config(key){
  return app_config[key]
}


function createWindow () {
    const win = new BrowserWindow({
      width: 1024,
      height: 768,
      webPreferences: {
        nodeIntegration: true,
        enableRemoteModule: true,
      },
    })
  
    win.loadFile('index.html',{
        query:{
            lang:read_config('defaultLanguage'),
            dev:is_dev ? '1' : '0',
            version:app.getVersion()
        }
    })

    if(is_dev){
      win.webContents.openDevTools()
    }

    win.removeMenu()
    win.webContents.on('new-window',new_window_event)
  }

let TMSG = undefined
{
  let translate_file_path = `code_translate/${read_config('defaultLanguage')}.js`
  eval(fs.readFileSync(translate_file_path,{encoding:'utf8'}))
  assert(TMSG != undefined,`Can't load translate file:${translate_file_path}`)
}

app.whenReady().then(createWindow)
app.on('second-instance', createWindow)

ipcMain.handle('change-language',(_e,lang)=>{
  write_config('defaultLanguage',lang)
})

ipcMain.handle('new-window',(_e)=>{
  createWindow()
})


let docs_callback_graph = fs.readdirSync("media/callbacks")
function is_callback_graph_url(url){
  for(const doc of docs_callback_graph){
    if(url.endsWith(doc))
      return true
  }
  return false
}

function new_window_event(event,url){
  if(is_callback_graph_url(url)){
    event.preventDefault()
    with(event.newGuest = new BrowserWindow()){
      removeMenu()
      loadURL(url)
      setTitle(TMSG["CALLBACK_GRAPH"]||"Callback Graph")
    }
  }
}