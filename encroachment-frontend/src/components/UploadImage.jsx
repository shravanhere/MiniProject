import { useState } from "react";
import { processAll } from "../services/api";

const UploadImage = () => {
  const [status, setStatus] = useState("");
  const [files, setFiles] = useState([]);

  const handleProcess = async () => {
    setStatus("Processing images & videos...");

    try {
      const data = await processAll();
      setStatus(data.status);
      setFiles(data.processed_files);
    } catch (err) {
      setStatus("Processing error");
      console.error(err);
    }
  };

  return (
    <div>
      <h3>Image / Video Processing</h3>
      <button onClick={handleProcess}>Start Processing</button>

      <p>{status}</p>

      <ul>
        {files.map((f, i) => (
          <li key={i}>{f}</li>
        ))}
      </ul>
    </div>
  );
};

export default UploadImage;
