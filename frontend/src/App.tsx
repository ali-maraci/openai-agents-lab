import { useState, useRef, useEffect } from 'react';
import { IconButton, TextField } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { sendMessage, Message } from './services/chatService';
import './App.scss';

const WELCOME_MESSAGE: Message = {
  role: 'ai',
  content: 'Hello! I can route you to the right specialist. Try math ("What is 145 * 37?"), unit conversions ("Convert 100 kg to pounds"), history questions ("When did the Roman Empire fall?"), or anything else!',
};

const AI_AVATAR = (
  <div className="avatar ai-avatar">
    <SmartToyIcon sx={{ fontSize: 28, color: '#2cb6aa' }} />
  </div>
);

export default function App() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!userInput.trim() || isLoading) return;

    const newUserMsg: Message = { role: 'user', content: userInput };
    const updatedMessages = [...messages, newUserMsg];
    setMessages(updatedMessages);
    setUserInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage(updatedMessages);
      setMessages(msgs => [...msgs, { role: 'ai', content: response }]);
    } catch (err) {
      console.error(err);
      setMessages(msgs => [...msgs, { role: 'ai', content: 'Connection Error: Unable to reach the backend.' }]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="brand-section">
          <div className="logo-container">
            <SmartToyIcon sx={{ fontSize: 40, color: '#1a2639' }} />
            <div className="logo-text">Agents Playground</div>
          </div>
          <div className="brand-divider" />
          <div className="subtitle">OPENAI AGENTS SDK</div>
        </div>
        <div className="header-links">
          <a
            href="https://github.com/ali-maraci/openai-agents-playground"
            target="_blank"
            rel="noopener noreferrer"
            className="github-link"
          >
            <svg height="24" viewBox="0 0 16 16" version="1.1" width="24" aria-hidden="true">
              <path
                fillRule="evenodd"
                d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
              />
            </svg>
            <span>GitHub</span>
          </a>
        </div>
      </header>

      <div className="chat-container">
        <div className="chat-history" ref={scrollRef}>
          {messages.map((msg, i) => (
            <div key={i} className={`message-wrapper ${msg.role}`}>
              {msg.role === 'ai' && AI_AVATAR}
              <div className="message-bubble">
                {msg.content}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-wrapper ai">
              {AI_AVATAR}
              <div className="message-bubble thinking-bubble">
                <div className="thinking-dots">
                  <span /><span /><span />
                </div>
                <span className="thinking-text">Thinking...</span>
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <TextField
            multiline
            maxRows={6}
            minRows={1}
            placeholder="Ask me anything..."
            value={userInput}
            onChange={e => setUserInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={isLoading}
            inputRef={inputRef}
            className="chat-input"
            sx={{
              width: '100%',
              '& .MuiOutlinedInput-root': {
                borderRadius: '28px',
                backgroundColor: '#ffffff',
                boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                alignItems: 'flex-end',
                paddingLeft: '16px',
                paddingRight: '8px',
                '& fieldset': { border: 'none' },
              },
              '& .MuiInputBase-input': {
                resize: 'none',
                marginTop: '14px',
                marginBottom: '14px',
                lineHeight: 1.5,
                overflowY: 'hidden',
                '&::placeholder': { color: '#94a3b8', opacity: 1 },
              },
              '& .MuiInputBase-inputMultiline': {
                paddingTop: 0,
                paddingBottom: 0,
              },
            }}
            slotProps={{
              input: {
                endAdornment: (
                  <IconButton
                    onClick={handleSend}
                    disabled={!userInput.trim() || isLoading}
                    color="primary"
                    sx={{ mb: '8px', flexShrink: 0 }}
                  >
                    <SendIcon />
                  </IconButton>
                ),
              },
            }}
          />
        </div>

        <footer className="app-footer">
          <p>&copy; 2026 Ali Maraci. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}
