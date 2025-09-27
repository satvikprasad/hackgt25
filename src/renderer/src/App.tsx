import '../globals.css'
import { useState } from 'react'

function App(): React.JSX.Element {
  // const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

  const [text, setText] = useState<string>('')
  const [isWorking, setIsWorking] = useState<boolean>(false)

  const BACKEND = 'http://127.0.0.1:5000'


  const sendMessage = async (): Promise<void> => {
    if (!text) return
    try {
      const res = await fetch(`${BACKEND}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })

      if (res.status === 202) {
        //const data = await res.json()
        // store a string representation so React doesn't try to render an object
        // disable input/button while job runs
        setIsWorking(true)
        setText('')
      } else {
        const err = await res.json().catch(() => ({}))
        console.error('sendMessage error', res.status, err)
        alert('Failed to start job: ' + (err.error || res.status))
      }
    } catch (e) {
      console.error(e)
      alert(e.toString())
    }
  }

  return (
    <>
      <div className="container">
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              placeholder={isWorking ? "" : "Type something here..."}
              value={text}
              onChange={(e) => setText((e.target as HTMLInputElement).value)}
              style={{ width: '100%', boxSizing: 'border-box' }}
              disabled={isWorking}
            />
            {isWorking && (
              <div className="dots-overlay" aria-hidden="true">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            )}
          </div>
          <button
            onClick={() => {
              if(isWorking) {
                setIsWorking(false)
              } else {
                sendMessage()
              }
            }}
            className={isWorking ? "cancel-btn" : "send-btn"}
            aria-label="Send"
            title="Send"
          >
            {isWorking ? (
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
                style={{ color: '#000000ff' }}
              >
                <path d="M6 6 L18 18" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                <path d="M6 18 L18 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              </svg>
            ) : (
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="currentColor"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path d="M2 21l21-9L2 3v7l15 2-15 2z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </>
  )
}

export default App
