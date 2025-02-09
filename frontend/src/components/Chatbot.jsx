import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ChatButton from "./ChatButton";
import { Message } from "./Message";
import axios from "axios";

export const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [hasShownWelcome, setHasShownWelcome] = useState(false); // New flag

  useEffect(() => {
    if (isOpen && !hasShownWelcome) {
      setMessages([{ role: "assistant", content: "Hi! How may I help you?" }]);
      setHasShownWelcome(true);
    }
  }, [isOpen, hasShownWelcome]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await axios.post("https://floating-chatbot-backend.onrender.com/chat", {
        question: input,
      });

      const assistantMessage = {
        role: "assistant",
        content: response.data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error communicating with server:", error);
    }

    setInput("");
  };

  return (
    <div className="fixed bottom-8 right-8 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.3 }}
            className="bg-gray-900 rounded-lg shadow-lg w-80 h-96 mb-4 flex flex-col"
          >
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message, index) => (
                <Message key={index} message={message} />
              ))}
            </div>
            <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
              <input
                type="text"
                value={input}
                onChange={handleInputChange}
                placeholder="Type your message..."
                className="w-full bg-gray-800 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </form>
          </motion.div>
        )}
      </AnimatePresence>
      <ChatButton isOpen={isOpen} onClick={() => setIsOpen(!isOpen)} />
    </div>
  );
};
