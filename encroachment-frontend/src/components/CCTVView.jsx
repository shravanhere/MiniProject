export default function CCTVView({ place }) {
  if (!place) return <p>Select location to view CCTV</p>;

  return (
    <div className="cctv">
      <h3>CCTV - {place}</h3>
      <video width="100%" controls>
        <source src="D:\Project\encroachment-frontend\src\data\cctvvideo.avi" type="video/mp4" />
      </video>
    </div>
  );
}
