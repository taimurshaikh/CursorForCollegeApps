import { useEffect, useMemo, useState } from "react";
import {
  createConversation,
  getMessages,
  listConversations,
  login,
  sendMessage,
  type Conversation,
  type Message,
  type Student,
} from "../lib/api";

function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : initial;
  });
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);
  return [value, setValue] as const;
}

export function App() {
  const [student, setStudent] = useLocalStorage<Student | null>(
    "student",
    null
  );
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useLocalStorage<
    number | null
  >("activeConversationId", null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!student) return;
    listConversations(student.id)
      .then(setConversations)
      .catch((error) => {
        // If student no longer exists in database, log them out
        console.error("Failed to load conversations:", error);
        setStudent(null);
        setActiveConversationId(null);
        setConversations([]);
        setMessages([]);
      });
  }, [student]);

  useEffect(() => {
    if (!activeConversationId) return;
    getMessages(activeConversationId)
      .then(setMessages)
      .catch(() => setMessages([]));
  }, [activeConversationId]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    try {
      const s = await login(email, name || "Student");
      setStudent(s);
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login failed. Please try again.");
    }
  }

  function handleLogout() {
    setStudent(null);
    setActiveConversationId(null);
    setConversations([]);
    setMessages([]);
    setEmail("");
    setName("");
  }

  async function newConversation() {
    if (!student) return;
    try {
      const conv = await createConversation(student.id);
      setConversations((prev) => [conv, ...prev]);
      setActiveConversationId(conv.id);
      setMessages([]);
    } catch (error) {
      console.error("Failed to create conversation:", error);
      // If student no longer exists, log them out
      if (
        error instanceof Error &&
        error.message.includes("Student not found")
      ) {
        handleLogout();
      }
    }
  }

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || !activeConversationId) return;
    const userLocal: Message = {
      id: Date.now(),
      conversation_id: activeConversationId,
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userLocal]);
    setInput("");
    setLoading(true);
    try {
      const assistant = await sendMessage(
        activeConversationId,
        userLocal.content
      );
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== userLocal.id),
        userLocal,
        assistant,
      ]);
    } catch (error) {
      console.error("Failed to send message:", error);
      // Remove the optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== userLocal.id));
      // If conversation no longer exists, refresh conversations
      if (
        error instanceof Error &&
        error.message.includes("Conversation not found")
      ) {
        setActiveConversationId(null);
        setMessages([]);
        // Try to refresh conversations list
        if (student) {
          listConversations(student.id)
            .then(setConversations)
            .catch(() => handleLogout());
        }
      }
    } finally {
      setLoading(false);
    }
  }

  if (!student) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
        <form
          onSubmit={handleLogin}
          className="w-full max-w-sm space-y-4 bg-white p-6 rounded-xl shadow"
        >
          <h1 className="text-xl font-semibold">Login</h1>
          <input
            className="w-full border rounded px-3 py-2"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="w-full border rounded px-3 py-2"
            placeholder="Name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
            Continue
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="h-screen grid grid-cols-12">
      <aside className="col-span-3 border-r bg-gray-50 flex flex-col">
        <div className="p-4 flex items-center justify-between">
          <div>
            <div className="font-semibold">{student.name}</div>
            <div className="text-xs text-gray-500">{student.email}</div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={newConversation}
              className="text-sm px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
            >
              New
            </button>
            <button
              onClick={handleLogout}
              className="text-sm px-3 py-1 rounded bg-gray-600 text-white hover:bg-gray-700"
            >
              Logout
            </button>
          </div>
        </div>
        <div className="overflow-y-auto">
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => setActiveConversationId(c.id)}
              className={`w-full text-left px-4 py-3 hover:bg-blue-50 ${
                activeConversationId === c.id ? "bg-blue-100" : ""
              }`}
            >
              {c.title}
            </button>
          ))}
        </div>
      </aside>
      <main className="col-span-9 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {!activeConversationId && (
            <div className="text-gray-500">
              Select or create a conversation to start.
            </div>
          )}
          {messages.map((m) => (
            <div
              key={m.id}
              className={`max-w-3xl ${m.role === "user" ? "ml-auto" : ""}`}
            >
              <div
                className={`rounded-2xl px-4 py-2 inline-block ${
                  m.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="text-gray-400 text-sm">Assistant is typing…</div>
          )}
        </div>
        <form onSubmit={handleSend} className="p-4 border-t flex gap-2">
          <input
            className="flex-1 border rounded px-3 py-2"
            placeholder="Type a message"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!activeConversationId}
          />
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
            disabled={!activeConversationId}
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
