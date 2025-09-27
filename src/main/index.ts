import { app, shell, BrowserWindow, ipcMain, globalShortcut, screen } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

app.commandLine.appendSwitch('enable-features', 'GlobalShortcutsPortal')

let mainWindow: BrowserWindow | undefined

function createWindow(): void {
    const winWidth = 900
    const winHeight = 100

    const display = screen.getPrimaryDisplay()
    const work = display.workArea
    const bottomOffset = 12
    const x = Math.round(work.x + (work.width - winWidth) / 2)
    const y = Math.round(work.y + work.height - winHeight - bottomOffset)

    mainWindow = new BrowserWindow({
        x,
        y,
        width: winWidth,
        height: winHeight,
        frame: false,
        show: false,
        transparent: true,
        autoHideMenuBar: true,
        movable: false,
        resizable: false,
        maximizable: false,
        fullscreenable: false,
        ...(process.platform === 'linux' ? { icon } : {}),
        webPreferences: {
            preload: join(__dirname, '../preload/index.js'),
            sandbox: false
        }
    })

    mainWindow.on('ready-to-show', () => {
        mainWindow!.show()
    })

    mainWindow.webContents.setWindowOpenHandler((details) => {
        shell.openExternal(details.url)
        return { action: 'deny' }
    })

    if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
    }
}

app.whenReady().then(() => {
    electronApp.setAppUserModelId('com.electron')

    // Default open or close DevTools by F12 in development
    // and ignore CommandOrControl + R in production.
    // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
    app.on('browser-window-created', (_, window) => {
        optimizer.watchWindowShortcuts(window)
    })

    // IPC test
    ipcMain.on('ping', () => console.log('pong'))

    createWindow()

    app.on('activate', function() {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })

const ret = globalShortcut.register('CommandOrControl+X', () => {
    if (mainWindow) {
        mainWindow.focus()
    }
})

if (!ret) {
    console.log('registration failed')
}

console.log(globalShortcut.isRegistered('CommandOrControl+X'))
})

app.on('will-quit', () => {
    globalShortcut.unregisterAll()
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
