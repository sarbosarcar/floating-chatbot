import { motion } from "framer-motion"
import { MessageCircle, X } from "lucide-react"
import PropTypes from 'prop-types';

const ChatButton = ({ isOpen, onClick }) => {
    return (
        <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={onClick}
            className="bg-blue-600 text-white rounded-full p-3 shadow-lg"
        >
            {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
        </motion.button>
    )
}

ChatButton.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClick: PropTypes.func.isRequired,
}

export default ChatButton;
