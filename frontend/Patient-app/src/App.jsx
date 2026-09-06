import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("Loading...");
  useEffect(() => {
    async function request() {
      try {
        const response = await axios.get("/api/api/v1/health");
        setMessage(response.data.status);
      } catch (e) {
        setMessage(e.status);
      }
    }
    request();
  }, []);
  return (
    <>
      <h1 className="text-3xl">Hello</h1>
      <p>{message}</p>
    </>
  );
}

export default App;
