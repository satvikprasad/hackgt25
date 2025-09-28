import { MicrophoneIcon } from "@heroicons/react/16/solid";
import "../globals.css";
import { useState, useRef, useEffect, useCallback } from "react";

import { io, Socket } from "socket.io-client";

interface Message {
  id: number;
  text: string;
  type: "message" | "error" | "complete";
  removing?: boolean;
};

function App(): React.JSX.Element {
  // const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')
  const socket = useRef<Socket | null>(null);

  const [text, setText] = useState<string>("");
  const [isWorking, setIsWorking] = useState<boolean>(false);
  const [messages, setMessages] = useState<
    Message[]
  >([]);

  useEffect(() => {
      window.electronAPI.setIgnore(isWorking);
    }, [isWorking]);


  useEffect(() => {
    socket.current = io("http://127.0.0.1:5000");

    socket.current.connect();

    socket.current.on("connect", () => {
      console.log("Connected to server");
    });

    socket.current.on(
      "query_response",
      ({ status }: { status: "complete" | "aborted" }) => {
        switch (status) {
          case "aborted":
          case "complete":
            setIsWorking(false);
            break;
        }
      },
    );

    socket.current.on(
      "transcribed_prompt",
      ({ prompt }: { prompt: string }) => {
        setText(prompt)

        sendMessage(prompt)
      }
    );

    socket.current.on(
      "error",
      ({ error }: { error: string }) => {
        addMessage(error, "error");
      }
    );

    socket.current.on(
      "complete",
      ({ message }: { message: string }) => {
        addMessage(message, "complete")
      }
    )

    socket.current.on("reassess", ({ response }: { response: string }) => {
      console.log(response);

      addMessage(response);
    });

    return () => {
      if (!socket.current) return;

      socket.current.disconnect();
    };
  }, []);

  const sendMessage = async (message: string): Promise<void> => {
    socket.current?.emit("query", message);

    setIsWorking(true);
  };

  const addMessage = useCallback((msg: string, type: "message" | "error" | "complete" = "message"): void => {
    const id = Date.now();
    setMessages((msgs) => [...msgs, { id, text: msg, type }]);

    if (type != "message") return;

    setTimeout(() => {
      setMessages((msgs) =>
        msgs.map((m) => (m.id === id ? { ...m, removing: true } : m)),
      );
      setTimeout(() => {
        setMessages((msgs) => msgs.filter((m) => m.id !== id));
      }, 500);
    }, 5000);
  }, []);

  const [recording, setRecording] = useState(false);

  return (
    <>
      <div style={{ justifyContent: "flex-end" }}>
        {messages.length > 0 &&
          messages.map((msg) => {
            let backgroundColor = "rgba(83, 78, 78, 0.9)"

            switch (msg.type) {
              case "message":
                break;
              case "error":
                backgroundColor = "rgba(255, 0, 0, 0.7)"
                break;
              case "complete":
                backgroundColor = "rgba(79, 171, 103, 0.7)"
                break;
            }

            return (
              <div
                className={`message-container ${msg.removing ? "removing" : ""} ${msg.type == "error" ? "error" : ""}`}
                style={{ marginBottom: "12px", backgroundColor: backgroundColor }}
                key={msg.id}
                onClick={() => {
                  if (msg.type == "message") return;

                  setMessages((msgs) => {
                    return msgs.reduce((acc, item) => {
                      if (item.id != msg.id) {
                        acc.push(item)
                      } else {
                        const copy = structuredClone(item)
                        copy.removing = true;

                        acc.push(copy)
                      }

                      return acc;
                    }, new Array<Message>());
                  })

                  setTimeout(() => {
                    setMessages((msgs) => {
                      return msgs.reduce((acc, item) => {
                        if (item.id != msg.id) {
                          acc.push(item)
                        }

                        return acc;
                      }, new Array<Message>());
                    })
                  }, 500);
                }}
              >
                <p>
                  <b>Gloo:</b> {msg.text}
                </p>
              </div>
            )
          })}
      </div>

      <div className="container">
        <form
          style={{ display: "flex", gap: 8, alignItems: "center" }}
          onSubmit={(e) => {
            e.preventDefault();

            sendMessage(text);
          }}
        >
          <button className="mic-btn" type="button" style={{
            color: !recording ? "#eeeeee" : "#ff5c85"
          }} onClick={(e) => {
            e.preventDefault();

            if (recording) {
              setRecording(false);

              socket.current?.emit("end-recording");
            } else {
              setRecording(true);

              socket.current?.emit("begin-recording");
            }
          }}>
            <MicrophoneIcon className="icon" />
          </button>
          <div style={{ position: "relative", flex: 1 }}>
            <input
              type="text"
              className="input-bar-container"
              placeholder={
                isWorking ? "" : "Type something here..."
              }
              value={recording ? "Press to stop recording..." : text}
              onChange={(e) =>
                setText((e.target as HTMLInputElement).value)
              }
              style={{ width: "100%", boxSizing: "border-box" }}
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
              onClick={(e) => {
                e.preventDefault();

                addMessage("Job cancelled");

                socket.current?.emit("abort");

                setIsWorking(false);
              }}
              className="cancel-btn"
              aria-label="Cancel"
              title="Cancel"
              type="button"
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
            <button
              className="send-btn"
              aria-label="Send"
              title="Send"
              type="submit"
            >
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
        </form>
      </div>
    </>
  );
}

export default App;
