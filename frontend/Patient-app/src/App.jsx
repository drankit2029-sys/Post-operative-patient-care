import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("Loading...");
  useEffect(() => {
    async function request() {
      try {
        const response = await axios.get("/api/message");
        setMessage(response.data.message);
      } catch (e) {
        setMessage(e.message);
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
