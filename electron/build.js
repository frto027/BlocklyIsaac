const packager = require('electron-packager')

async function bundleElectronApp(options) {
  const appPaths = await packager(options)
  console.log(`Electron app bundles created:\n${appPaths.join("\n")}`)
}

bundleElectronApp(
    {
        dir:'.',
        out:'out',
        icon:'favicon.ico'
    }
)