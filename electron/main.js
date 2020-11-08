const { app, BrowserWindow, ipcMain } = require("electron")
const fs = require("fs")
const path = require("path")

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
        enableRemoteModule: true
      },
      autoHideMenuBar:true
    })
  
    win.loadFile('index.html',{
        query:{
            lang:read_config('defaultLanguage'),
            dev:is_dev ? '1' : '0'
        }
    })

    if(is_dev){
      win.webContents.openDevTools()
    }

  }

app.whenReady().then(createWindow)

ipcMain.handle('change-language',(_e,lang)=>{
  write_config('defaultLanguage',lang)
})
