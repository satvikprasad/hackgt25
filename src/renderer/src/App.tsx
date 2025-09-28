import { ChevronDoubleRightIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import "../globals.css";
import { useState, useRef, useEffect, useCallback } from "react";

import { io, Socket } from 'socket.io-client'

function App(): React.JSX.Element {
  // const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')
  const socket = useRef<Socket | null>(null)

  const [text, setText] = useState<string>('')
  const [isWorking, setIsWorking] = useState<boolean>(false)
<<<<<<< HEAD
  const [messages, setMessages] = useState<{ id: number; text: string; removing?: boolean }[]>([])
=======
  const [messages, setMessages] = useState<{ id: number; text: string, removing?: boolean }[]>([])
>>>>>>> 80214e1 (t)

  useEffect(() => {
    socket.current = io('http://127.0.0.1:5000')

<<<<<<< HEAD
    socket.current.connect()

    socket.current.on('connect', () => {
      console.log('Connected to server')
    })

    socket.current.on('query_response', ({ status }: { status: 'complete' | 'aborted' }) => {
      switch (status) {
        case 'aborted':
        case 'complete':
          setIsWorking(false)
          break
      }
    })

    socket.current.on('reassess', ({ response }: { response: string }) => {
      console.log(response)

      addMessage(response)
    })

    return () => {
      if (!socket.current) return

      socket.current.disconnect()
    }
  }, [])

=======
>>>>>>> 80214e1 (t)
  const sendMessage = async (): Promise<void> => {
    socket.current?.emit('query', text)

<<<<<<< HEAD
    setIsWorking(true)
  }

  const addMessage = useCallback((msg: string): void => {
    const id = Date.now()
    setMessages((msgs) => [...msgs, { id, text: msg }])

        setTimeout(() => {
            setMessages((msgs) =>
                        msgs.map((m) => (m.id === id ? { ...m, removing: true } : m))
                       )
                       setTimeout(() => {
                           setMessages((msgs) => msgs.filter((m) => m.id !== id))
                       }, 500)
        }, 5000)
    }, []);

  useEffect(() => {
    console.log(messages)
  }, [messages])
=======
      if (res.status === 202) {
        const data = await res.json()
        // store a string representation so React doesn't try to render an object
        // disable input/button while job runs

        addMessage(`Job started: ${data.message}`)

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

  const addMessage = (msg: string): void => {
    const id = Date.now()
    setMessages((msgs) => [...msgs, { id, text: msg }])

    // Auto-remove with fade-out after 5s
    setTimeout(() => {
      setMessages((msgs) =>
        msgs.map((m) => (m.id === id ? { ...m, removing: true } : m))
      )
      setTimeout(() => {
        setMessages((msgs) => msgs.filter((m) => m.id !== id))
      }, 500)
    }, 5000)
  }
>>>>>>> 80214e1 (t)

  return (
    <>
      <div style={{ justifyContent: 'flex-end' }}>
        {messages.length > 0 &&
          messages.map((msg) => (
            <div
<<<<<<< HEAD
              className={`message-container ${msg.removing ? 'removing' : ''}`}
              style={{ marginBottom: '12px' }}
              key={msg.id}
            >
              <p>
                <b>Gloo:</b> {msg.text}
              </p>
=======
              className={`message-container ${msg.removing ? "removing" : ""}`}
              style={{ marginBottom: '12px' }}
              key={msg.id}
            >
              <p>{msg.text}</p>
>>>>>>> 80214e1 (t)
            </div>
          ))}
      </div>

      <div className="container">
        <form
          style={{ display: 'flex', gap: 8, alignItems: 'center' }}
          onSubmit={(e) => {
            e.preventDefault()

            sendMessage()
          }}
        >
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              className="input-bar-container"
              placeholder={isWorking ? '' : 'Type something here...'}
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
          {isWorking ? (
            <button
<<<<<<< HEAD
              onClick={(e) => {
                e.preventDefault()

                addMessage('Job cancelled')

                socket.current?.emit('abort')

=======
              onClick={() => {

                addMessage('Job cancelled')
>>>>>>> 80214e1 (t)
                setIsWorking(false)
              }}
              className="cancel-btn"
              aria-label="Cancel"
              title="Cancel"
<<<<<<< HEAD
              type="button"
=======
>>>>>>> 80214e1 (t)
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M18.3 5.71a1 1 0 0 0-1.41 0L12 10.59 7.11 5.7A1 1 0 0 0 5.7 7.11L10.59 12l-4.89 4.89a1 1 0 1 0 1.41 1.41L12 13.41l4.89 4.89a1 1 0 0 0 1.41-1.41L13.41 12l4.89-4.89a1 1 0 0 0 0-1.4z" />
              </svg>
            </button>
          ) : (
<<<<<<< HEAD
            <button className="send-btn" aria-label="Send" title="Send" type="submit">
=======
            <button onClick={sendMessage} className="send-btn" aria-label="Send" title="Send">
>>>>>>> 80214e1 (t)
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
            </button>
          )}
<<<<<<< HEAD
        </form>
=======
        </div>
>>>>>>> 80214e1 (t)
      </div>
    </>
  )
}

export default App
