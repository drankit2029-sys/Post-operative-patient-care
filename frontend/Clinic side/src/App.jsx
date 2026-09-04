import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("/api/")
      .then((response) => response.json())
      .then((data) => setMessage(data.message))
      .catch((error) => window.alert(error));
  }, []);

  return (
    <main>
      <div className="bg-red-300">
        <h1 className="text-2xl">FastAPI + React App</h1>
        <p>{message}</p>
      </div>
    </main>
  );
}

export default App;
