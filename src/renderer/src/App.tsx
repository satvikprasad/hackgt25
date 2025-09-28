import { ChevronDoubleRightIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import "../globals.css";
import { useState, useRef, useEffect, useCallback } from "react";

import { io, Socket } from "socket.io-client";

function App(): React.JSX.Element {
    // const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')
    const socket = useRef<Socket | null>(null);

    const [text, setText] = useState<string>("");
    const [isWorking, setIsWorking] = useState<boolean>(false);
    const [messages, setMessages] = useState<
        { id: number; text: string; removing?: boolean }[]
    >([]);

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

        socket.current.on("reassess", ({ response }: { response: string }) => {
            console.log(response);

            addMessage(response);
        });

    return () => {
      if (!socket.current) return

            socket.current.disconnect();
        };
    }, []);

    const sendMessage = async (): Promise<void> => {
        socket.current?.emit("query", text);

        setIsWorking(true);
    };

    const addMessage = useCallback((msg: string): void => {
        const id = Date.now();
        setMessages((msgs) => [...msgs, { id, text: msg }]);

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
        console.log(messages);
    }, [messages]);

    return (
        <>
            <div style={{ justifyContent: "flex-end" }}>
                {messages.length > 0 &&
                    messages.map((msg) => (
                        <div
                            className={`message-container ${msg.removing ? "removing" : ""}`}
                            style={{ marginBottom: "12px" }}
                            key={msg.id}
                        >
                            <p>
                                <b>Gloo:</b> {msg.text}
                            </p>
                        </div>
                    ))}
            </div>

            <div className="container">
                <form style={{ display: "flex", gap: 8, alignItems: "center" }} onSubmit={(e) => {
                    e.preventDefault()

                    sendMessage();
                }}>
                    <div style={{ position: "relative", flex: 1 }}>
                        <input
                            type="text"
                            className="input-bar-container"
                            placeholder={
                                isWorking ? "" : "Type something here..."
                            }
                            value={text}
                            onChange={(e) =>
                                setText((e.target as HTMLInputElement).value)
                            }
                            style={{ width: "100%", boxSizing: "border-box", color: isWorking ? "rgb(180, 180, 180)" : "white" }}
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
                                e.preventDefault()

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
                            <ChevronDoubleRightIcon style={{
                                height: "20px",
                            }}/>
                        </button>
                    )}
                </form>
            </div>
        </>
    );
}

export default App;
