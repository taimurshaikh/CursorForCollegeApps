export type Student = {
  id: number;
  email: string;
  name: string;
};

export type Conversation = {
  id: number;
  student_id: number;
  title: string;
};

export type Message = {
  id: number;
  conversation_id: number;
  role: "user" | "assistant";
  content: string;
};

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function login(email: string, name?: string): Promise<Student> {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, name }),
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}

export async function listConversations(
  studentId: number
): Promise<Conversation[]> {
  const res = await fetch(`${BASE_URL}/conversations/${studentId}`);
  if (!res.ok) throw new Error("Failed to load conversations");
  const data = await res.json();
  return data.conversations;
}

export async function createConversation(
  studentId: number,
  title?: string
): Promise<Conversation> {
  const res = await fetch(`${BASE_URL}/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: studentId, title }),
  });
  if (!res.ok) throw new Error("Failed to create conversation");
  return res.json();
}

export async function getMessages(conversationId: number): Promise<Message[]> {
  const res = await fetch(
    `${BASE_URL}/conversations/${conversationId}/messages`
  );
  if (!res.ok) throw new Error("Failed to load messages");
  const data = await res.json();
  return data.messages;
}

export async function sendMessage(
  conversationId: number,
  content: string
): Promise<Message> {
  const res = await fetch(
    `${BASE_URL}/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    }
  );
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}
