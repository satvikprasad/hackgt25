import '../globals.css';
import { useState } from 'react'

function App(): React.JSX.Element {
  // const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

  const [text, setText] = useState<string>('')

  return (
    <>
      <div className="container">
        <input
          type="text"
          placeholder='Type something here...'
          value={text}
          onChange={(e) => setText((e.target as HTMLInputElement).value)}
        />
        <button></button>
      </div>
    </>
  )
}

export default App
