import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function MapView({ location }) {
  if (!location) return <p>Select a location</p>;

  return (
    <MapContainer center={[location.lat, location.lng]} zoom={14} className="map">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Marker position={[location.lat, location.lng]}>
        <Popup>{location.name}</Popup>
      </Marker>
    </MapContainer>
  );
}

