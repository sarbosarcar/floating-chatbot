import { Chatbot } from "./components/Chatbot"
import "./App.css"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-950 text-white w-[100vw]">
      <h1 className="text-4xl font-bold mb-8">Welcome to <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 animate-text font-bold">Srijan&apos;25</span></h1>
      <p className="text-xl mb-4">Click the chat button to start a conversation</p>
      <p>with our <span className="bg-clip-text text-transparent bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 animate-text font-bold">AI Assistant</span></p>
      <Chatbot />
    </main>
  )
}

