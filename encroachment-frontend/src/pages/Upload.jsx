import UploadImage from "../components/UploadImage";


function Upload() {
  return (
    <div>
      <h1>Upload Surveillance Data</h1>

      <select>
        <option>CCTV</option>
        <option>Drone</option>
        <option>Image</option>
      </select>
      <div className="layout">
      <Sidebar />
      <div className="content">
        <h2>Upload Data</h2>

      <input type="file" />
      <button>Submit</button>
      </div>
      </div>
    </div>
  );
}

export default Upload;
