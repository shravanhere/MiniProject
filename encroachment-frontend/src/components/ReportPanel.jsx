function ReportPanel() {
  return (
    <div className="card">
      <h3>Detected Encroachments</h3>
      <table width="100%" border="1" cellPadding="8">
        <thead>
          <tr>
            <th>ID</th>
            <th>Location</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>ENC-001</td>
            <td>Coimbatore City</td>
            <td>Pending Verification</td>
          </tr>
          <tr>
            <td>ENC-002</td>
            <td>Whitefield Area</td>
            <td>Verified</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default ReportPanel;
