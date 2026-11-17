import { useState } from "react";

function FileUpload({ onDataLoaded }) {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      setMessage(result.message);

      // Temporary preview
      onDataLoaded([
        {
          filename: result.filename,
          status: "Uploaded Successfully",
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessage("Upload Failed");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "40px" }}>
      <input
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br />
      <br />

      <button onClick={uploadFile}>
        Upload Dataset
      </button>

      <h3>{message}</h3>
    </div>
  );
}

export default FileUpload;