import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("https://4zrh6x-8000.csb.app/")
      .then((response) => response.json())
      .then((data) => setMessage(data.message))
      .catch((error) => window.alert(error));
  }, []);

  return (
    <main>
      <h1>FastAPI + React App</h1>
      <p>{message}</p>
    </main>
  );
}

export default App;
