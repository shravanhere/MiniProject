import Sidebar from "../components/Sidebar";

export default function Dashboard() {
  return (
    <div className="layout">
      <Sidebar />
      <div className="content">
        <h2>Dashboard Loaded Successfully</h2>
        <p>If you see this, routing is correct.</p>
      </div>
    </div>
  );
}
