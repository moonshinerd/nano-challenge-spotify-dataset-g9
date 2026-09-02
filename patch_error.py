import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = "function App() {"
replacement = """function App() {
  const [errorMsg, setErrorMsg] = useState(null);
  
  useEffect(() => {
    const handleErr = (msg, url, line, col, error) => {
      setErrorMsg(`${msg} - ${error?.stack}`);
      return false; 
    };
    window.onerror = handleErr;
    window.addEventListener('unhandledrejection', (e) => {
      setErrorMsg(`Unhandled Promise Rejection: ${e.reason?.message} - ${e.reason?.stack}`);
    });
  }, []);
  
  if (errorMsg) {
    return (
      <div className="bg-red-900 text-white p-10 h-screen w-screen overflow-auto">
        <h1 className="text-4xl font-bold">CRASH FATAL!</h1>
        <pre className="mt-4 whitespace-pre-wrap">{errorMsg}</pre>
        <button onClick={() => window.location.reload()} className="mt-4 bg-white text-black px-4 py-2 rounded">Reload</button>
      </div>
    );
  }
"""

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
