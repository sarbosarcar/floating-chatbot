// import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';

export const Message = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
        >
            <div
                className={`max-w-xs px-4 py-2 rounded-lg ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300'}`}
            >
                {message.content}
            </div>
        </motion.div>
    );
};

Message.propTypes = {
    message: PropTypes.shape({
        role: PropTypes.oneOf(['user', 'assistant']).isRequired,
        content: PropTypes.string.isRequired,
    }).isRequired,
};
